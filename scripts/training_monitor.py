#!/usr/bin/env python3
"""
Training completion monitor.

Polls RunPod every N minutes. When a pod's GPU goes idle after being active:
  1. Downloads the adapter from HuggingFace to local machine
  2. Sends a Telegram message confirming both are done

State is tracked in ~/.ronin48_training_state.json so it survives restarts.

Usage:
  python3 training_monitor.py
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import os

import requests

RUNPOD_KEY = os.environ["RUNPOD_KEY"]
HF_TOKEN   = os.environ["HF_TOKEN"]
TG_TOKEN   = os.environ["TG_TOKEN"]
TG_CHAT    = os.environ["TG_CHAT"]
RUNPOD_URL = f"https://api.runpod.io/graphql?api_key={RUNPOD_KEY}"
STATE_FILE = Path.home() / ".ronin48_training_state.json"
ADAPTER_BASE = Path.home() / "Source/adapters"

ADAPTERS = {
    "ABBY":  {"hf_repo": "Ronin48LLC/abby-lora-adapter",  "local": ADAPTER_BASE / "abby"},
    "SELMA": {"hf_repo": "Ronin48LLC/selma-lora-adapter", "local": ADAPTER_BASE / "selma"},
    "BONES": {"hf_repo": "Ronin48LLC/bones-lora-adapter", "local": ADAPTER_BASE / "bones"},
    "BRUNO": {"hf_repo": "Ronin48LLC/bruno-lora-adapter", "local": ADAPTER_BASE / "bruno"},
}

IDLE_THRESHOLD = 10  # GPU% below this = idle


def gql(query, variables=None):
    resp = requests.post(
        RUNPOD_URL,
        json={"query": query, "variables": variables or {}},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data.get("data", {})


def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT, "text": msg},
            timeout=10,
        )
    except Exception as e:
        print(f"Telegram send failed: {e}", file=sys.stderr)


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def detect_model(pod_name):
    for model in ADAPTERS:
        if model in pod_name.upper():
            return model
    return None


def download_adapter(model):
    cfg = ADAPTERS[model]
    cfg["local"].mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "hf", "download", cfg["hf_repo"],
            "--local-dir", str(cfg["local"]),
            "--token", HF_TOKEN,
        ],
        check=True,
        capture_output=True,
    )
    return cfg["local"]


def main():
    state = load_state()

    pods = gql(
        "{ myself { pods { id name desiredStatus runtime { gpus { gpuUtilPercent } uptimeInSeconds } } } }"
    ).get("myself", {}).get("pods", [])

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Checking {len(pods)} pod(s)...")

    for pod in pods:
        pid  = pod["id"]
        name = pod.get("name", "unknown")
        rt   = pod.get("runtime") or {}
        gpus = rt.get("gpus") or []
        util = gpus[0]["gpuUtilPercent"] if gpus else 0
        uptime_h = rt.get("uptimeInSeconds", 0) // 3600

        ps = state.setdefault(pid, {
            "name": name,
            "was_active": False,
            "complete": False,
            "downloaded": False,
        })

        print(f"  {name} [{pid}] — GPU {util}% | {uptime_h}h up | active={ps['was_active']}")

        if util > IDLE_THRESHOLD:
            ps["was_active"] = True

        # Use state name (set manually) for detection, fall back to live pod name
        detect_name = ps.get("name", name)

        if ps["was_active"] and util <= IDLE_THRESHOLD and not ps["complete"]:
            model = detect_model(detect_name)
            if not model:
                print(f"  Could not detect model from name '{detect_name}' — skipping")
                continue

            ps["complete"] = True
            ps["completed_at"] = datetime.now().isoformat()
            print(f"  {model} training complete!")
            send_telegram(f"Training complete for {model}. Downloading adapter from HuggingFace...")

        if ps["complete"] and not ps["downloaded"]:
            model = detect_model(detect_name)
            if not model:
                continue
            try:
                local_path = download_adapter(model)
                ps["downloaded"] = True
                ps["downloaded_at"] = datetime.now().isoformat()
                ps["local_path"] = str(local_path)
                msg = (
                    f"✅ {model} done.\n"
                    f"HuggingFace: {ADAPTERS[model]['hf_repo']}\n"
                    f"Local: {local_path}"
                )
                send_telegram(msg)
                print(f"  {model} adapter downloaded to {local_path}")
            except subprocess.CalledProcessError as e:
                err = e.stderr.decode() if e.stderr else str(e)
                send_telegram(f"⚠️ {model} training done but download failed:\n{err[:300]}")
                print(f"  Download failed: {err}", file=sys.stderr)

    save_state(state)
    print(f"State saved to {STATE_FILE}")


if __name__ == "__main__":
    main()
