#!/usr/bin/env python3
"""
RunPod training monitor with auto-queue.

Monitors a running pod for training completion (GPU goes idle), terminates it,
then automatically deploys the next model in the queue.

Queue: SELMA → ABBY → (pause, check balance before ATTICUS)

Usage:
  python3 runpod_monitor.py [pod_id]
"""

import json
import sys
import time
from datetime import datetime

import requests

RUNPOD_API_KEY = "RUNPOD_KEY_REDACTED"
HF_TOKEN       = "HF_TOKEN_REDACTED"
API_URL        = f"https://api.runpod.io/graphql?api_key={RUNPOD_API_KEY}"
TEMPLATE_ID    = "runpod-torch-v220"

POLL_INTERVAL      = 300  # 5 minutes
IDLE_THRESHOLD     = 10   # GPU % below this = idle
IDLE_CONFIRMATIONS = 2    # consecutive idle checks before terminating

GPU_PREFERENCE = [
    "NVIDIA A100 80GB PCIe",
    "NVIDIA A100-SXM4-80GB",
    "NVIDIA A100-SXM4-40GB",
]

# Training queue — name, repo URL, train command
TRAINING_QUEUE = [
    {
        "name": "ABBY",
        "repo": "https://codeberg.org/Ronin48/ABBY.git",
        "cmd": "git clone https://codeberg.org/Ronin48/ABBY.git && cd ABBY && python3 scripts/training/train_qlora.py --config configs/training_config.yaml",
    },
    # ATTICUS queued manually after checking balance
]


def gql(query, variables=None):
    resp = requests.post(API_URL, json={"query": query, "variables": variables or {}}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise Exception(data["errors"])
    return data.get("data", {})


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def get_pod(pod_id):
    return gql("""
        query pod($id: String!) {
          pod(input: {podId: $id}) {
            id name desiredStatus
            runtime {
              gpus { gpuUtilPercent memoryUtilPercent }
              uptimeInSeconds
            }
          }
        }
    """, {"id": pod_id}).get("pod")


def terminate_pod(pod_id):
    return gql("""
        mutation terminate($id: String!) {
          podTerminate(input: {podId: $id})
        }
    """, {"id": pod_id})


def get_balance():
    try:
        data = gql("{ myself { currentSpendPerHr spendLimit } }")
        me = data.get("myself", {})
        return me.get("spendLimit", 0), me.get("currentSpendPerHr", 0)
    except Exception:
        return None, None


def deploy_pod(model_name, train_cmd):
    """Deploy a new training pod for the given model."""
    log(f"Deploying {model_name} training pod...")

    for gpu_id in GPU_PREFERENCE:
        mutation = """
        mutation {
          podFindAndDeployOnDemand(input: {
            name: \"""" + model_name + """-Training",
            gpuTypeId: \"""" + gpu_id + """\",
            gpuCount: 1,
            volumeInGb: 100,
            containerDiskInGb: 50,
            templateId: \"""" + TEMPLATE_ID + """\",
            env: [{key: "HF_TOKEN", value: \"""" + HF_TOKEN + """\"}],
            ports: "22/tcp"
          }) {
            id name costPerHr
            machine { gpuDisplayName }
          }
        }
        """
        try:
            result = gql(mutation)
            pod = result.get("podFindAndDeployOnDemand")
            if pod and pod.get("id"):
                log(f"✓ {model_name} pod deployed — ID: {pod['id']} | GPU: {pod.get('machine',{}).get('gpuDisplayName','A100')} | ${pod.get('costPerHr',0):.2f}/hr")
                return pod["id"]
            log(f"  {gpu_id} — no availability, trying next...")
        except Exception as e:
            if "SUPPLY_CONSTRAINT" in str(e):
                log(f"  {gpu_id} — supply constraint, trying next...")
            else:
                log(f"  {gpu_id} — error: {e}")

    log(f"ERROR: No A100 GPUs available for {model_name}. Top up credits and retry manually.")
    return None


def wait_for_running(pod_id, model_name, timeout=180):
    """Wait for pod to reach RUNNING state."""
    log(f"Waiting for {model_name} pod to start...")
    for _ in range(timeout):
        try:
            pod = get_pod(pod_id)
            if pod and pod.get("desiredStatus") == "RUNNING":
                log(f"✓ {model_name} pod is RUNNING")
                return True
        except Exception:
            pass
        time.sleep(10)
    log(f"WARNING: {model_name} pod did not reach RUNNING state in time — monitor anyway")
    return False


def monitor_pod(pod_id, model_name):
    """Monitor a pod until GPU goes idle, then terminate. Returns True if completed cleanly."""
    log(f"Monitoring {model_name} pod {pod_id} — polling every {POLL_INTERVAL//60} min")

    gpu_was_active = False
    idle_count = 0

    while True:
        try:
            pod = get_pod(pod_id)
            if not pod:
                log(f"{model_name}: pod not found — may have already terminated.")
                return True

            status = pod.get("desiredStatus", "UNKNOWN")
            runtime = pod.get("runtime") or {}
            gpus = runtime.get("gpus") or []
            uptime = runtime.get("uptimeInSeconds", 0)
            h, m = uptime // 3600, (uptime % 3600) // 60

            if gpus:
                util = gpus[0].get("gpuUtilPercent", 0)
                mem  = gpus[0].get("memoryUtilPercent", 0)
                log(f"{model_name} | {status} | GPU {util}% | VRAM {mem}% | {h}h{m}m")
            else:
                util = 0
                log(f"{model_name} | {status} | no GPU data | {h}h{m}m")

            if status not in ("RUNNING", "EXITED"):
                log(f"{model_name}: pod status is {status} — stopping monitor.")
                return False

            if util > IDLE_THRESHOLD:
                gpu_was_active = True
                idle_count = 0
                log(f"{model_name}: training active.")
            elif gpu_was_active:
                idle_count += 1
                log(f"{model_name}: GPU idle ({idle_count}/{IDLE_CONFIRMATIONS}).")
                if idle_count >= IDLE_CONFIRMATIONS:
                    log(f"{model_name}: training complete — terminating pod.")
                    terminate_pod(pod_id)
                    log(f"{model_name}: pod terminated.")
                    return True
            else:
                log(f"{model_name}: GPU not yet active — waiting for training to start.")

        except Exception as e:
            log(f"Error: {e}")

        time.sleep(POLL_INTERVAL)


def run_queue(selma_pod_id):
    # ── Step 1: Monitor SELMA ────────────────────────────────────────
    monitor_pod(selma_pod_id, "SELMA")

    # ── Step 2: Auto-queue ABBY ──────────────────────────────────────
    for job in TRAINING_QUEUE:
        name = job["name"]
        log(f"")
        log(f"{'='*60}")
        log(f"Starting {name} training run")
        log(f"{'='*60}")

        pod_id = deploy_pod(name, job["cmd"])
        if not pod_id:
            log(f"Could not deploy {name} — stopping queue.")
            break

        wait_for_running(pod_id, name)

        # Give it 10 min to pull weights and start training before first check
        log(f"{name}: waiting 10 min for weights to load before first GPU check...")
        time.sleep(600)

        monitor_pod(pod_id, name)

    # ── Step 3: Balance check before ATTICUS ────────────────────────
    log("")
    log("="*60)
    log("ABBY training complete. Checking balance before ATTICUS...")
    balance, spend_rate = get_balance()
    if balance is not None:
        log(f"Remaining credit: ${balance:.2f} | Current spend rate: ${spend_rate:.2f}/hr")
        if balance >= 20:
            log("✓ Sufficient balance for ATTICUS training (~$15-25).")
            log("To queue ATTICUS, run:")
            log("  python3 scripts/runpod_monitor.py --atticus")
        else:
            log(f"⚠ Balance ${balance:.2f} may be too low for ATTICUS 70B training.")
            log("Top up RunPod credits then run:")
            log("  python3 scripts/runpod_monitor.py --atticus")
    else:
        log("Could not fetch balance — check runpod.io/console/billing manually.")

    log("Queue complete.")


def run_atticus():
    """Deploy and monitor ATTICUS training only."""
    atticus = {
        "name": "ATTICUS",
        "repo": "https://codeberg.org/Ronin48/ATTICUS.git",
        "cmd": "git clone https://codeberg.org/Ronin48/ATTICUS.git && cd ATTICUS && python3 scripts/training/train_qlora.py --config configs/training_config.yaml",
    }
    pod_id = deploy_pod(atticus["name"], atticus["cmd"])
    if not pod_id:
        sys.exit(1)
    wait_for_running(pod_id, "ATTICUS")
    log("ATTICUS: waiting 10 min for weights to load...")
    time.sleep(600)
    monitor_pod(pod_id, "ATTICUS")
    log("ATTICUS training complete.")


if __name__ == "__main__":
    if "--atticus" in sys.argv:
        run_atticus()
    else:
        pod_id = next((a for a in sys.argv[1:] if not a.startswith("--")), "xe7a00jq4myu69")
        run_queue(pod_id)
