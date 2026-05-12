#!/usr/bin/env python3
"""
SELMA RunPod Auto-Deploy
Spins up an A100-80GB pod and SSHes you in automatically.
"""

import os
import sys
import json
import time
import subprocess
from urllib.request import Request, urlopen
from urllib.error import HTTPError

RUNPOD_API = "https://api.runpod.io/graphql"
# Constants for pod deployment
TEMPLATE_ID = "runpod-torch-v220"
IMAGE_NAME = "runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04"


def call_api(query, variables=None):
    """Call RunPod GraphQL API."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("ERROR: RUNPOD_API_KEY not set")
        sys.exit(1)

    data = json.dumps(payload).encode()
    url = RUNPOD_API + "?api_key=" + api_key
    req = Request(url, data=data, headers={
        "Content-Type": "application/json",
        "User-Agent": "curl/7.81.0"
    })

    try:
        with urlopen(req) as resp:
            result = json.loads(resp.read())
            if "errors" in result:
                raise Exception(f"API error: {result['errors']}")
            return result.get("data", {})
    except HTTPError as e:
        raise Exception(f"HTTP {e.code}: {e.read().decode()}")


def get_templates():
    """Fetch list of available templates from RunPod."""
    # Try common template query names
    for query_name in ["podTemplates", "templates"]:
        query = f"{{ {query_name} {{ id name }} }}"
        try:
            result = call_api(query)
            if result and query_name in result:
                return result.get(query_name, [])
        except Exception:
            # Try next query name
            continue
    return []


def get_images():
    """Fetch list of available images (if supported)."""
    # RunPod API may not expose a direct images list; placeholder for future.
    return []


def validate_template_and_image():
    """Validate that the specified template ID and image name are available."""
    print("Validating template and image...")
    
    # Check template
    templates = get_templates()
    template_ids = [t.get("id") for t in templates if t.get("id")]
    template_names = [t.get("name") for t in templates if t.get("name")]
    
    if TEMPLATE_ID not in template_ids and TEMPLATE_ID not in template_names:
        print(f"WARNING: Template '{TEMPLATE_ID}' not found in available templates.")
        print(f"Available templates (ID/Name):")
        for t in templates[:10]:  # Show first 10
            tid = t.get("id", "N/A")
            tname = t.get("name", "N/A")
            print(f"  ID: {tid}, Name: {tname}")
        if len(templates) > 10:
            print(f"  ... and {len(templates) - 10} more")
        # Don't exit - just warn, as the API might accept it anyway
    
    # Note: Image validation is harder as RunPod API may not expose image lists
    # We'll just note that we're using the specified image
    print(f"Using template: {TEMPLATE_ID}")
    print(f"Using image: {IMAGE_NAME}")
    print()


def try_deploy(gpu_id, hf_token):
    """Attempt to deploy a pod with the given GPU type. Returns pod dict or None."""
    deploy_query = """
    mutation {
      podFindAndDeployOnDemand(input: {
        name: "SELMA-Training",
        gpuTypeId: """ + '"' + gpu_id + '"' + """,
        gpuCount: 1,
        volumeInGb: 100,
        containerDiskInGb: 50,
        templateId: """ + '"' + TEMPLATE_ID + '"' + """,
        env: [{key: "HF_TOKEN", value: """ + '"' + hf_token + '"' + """}],
        ports: "22/tcp"
      }) {
        id
        name
        gpuCount
        costPerHr
        machine {
          gpuDisplayName
        }
        runtime {
          ports {
            ip
            isIpPublic
            publicPort
            privatePort
          }
        }
      }
    }
    """
    try:
        result = call_api(deploy_query)
        return result.get("podFindAndDeployOnDemand")
    except Exception as e:
        if "SUPPLY_CONSTRAINT" in str(e):
            return None
        raise


def deploy_pod(hf_token):
    """Deploy A100 pod with HF_TOKEN, trying GPU options in preference order."""
    # Preference order: A100 PCIe 80GB → A100 SXM 80GB → A100 SXM 40GB
    GPU_PREFERENCE = [
        ("NVIDIA A100 80GB PCIe",    "A100 PCIe 80GB"),
        ("NVIDIA A100-SXM4-80GB",    "A100 SXM 80GB"),
        ("NVIDIA A100-SXM4-40GB",    "A100 SXM 40GB"),
    ]

    pod = None
    for gpu_id, gpu_label in GPU_PREFERENCE:
        print(f"Trying {gpu_label}...")
        pod = try_deploy(gpu_id, hf_token)
        if pod:
            print(f"✓ Pod created on {gpu_label}")
            break
        print(f"  No availability — trying next option...")

    if not pod or not pod.get("id"):
        print("ERROR: No A100 GPUs available. Try again later or use the RunPod web console.")
        sys.exit(1)

    pod_id = pod["id"]
    print(f"  Pod ID: {pod_id}")
    print(f"  GPU: {pod.get('machine', {}).get('gpuDisplayName', 'A100')}")
    print(f"  Cost: ${pod.get('costPerHr', 0):.2f}/hr")
    print()

    # Wait for SSH to be ready
    print("Waiting for pod to be ready (this takes ~2-3 min)...")
    for attempt in range(60):
        time.sleep(3)
        status_query = f"""
        query {{
          pod(input: {{ podId: "{pod_id}" }}) {{
            id
            desiredStatus
            runtime {{
              ports {{
                ip
                isIpPublic
                publicPort
                privatePort
              }}
            }}
          }}
        }}
        """
        result = call_api(status_query)
        pod_status = result.get("pod", {})
        current_status = pod_status.get("desiredStatus", "unknown")

        if current_status == "RUNNING":
            ports = pod_status.get("runtime", {}).get("ports", [])
            if ports and ports[0].get("publicPort"):
                return pod_id, ports[0]["ip"], ports[0]["publicPort"]

        print(f"  {attempt+1}/60 - Status: {current_status}")

    print("ERROR: Pod didn't become ready in time")
    sys.exit(1)


def ssh_into_pod(ip, port):
    """SSH into the pod and run training."""
    print()
    print("✓ Pod is ready!")
    print(f"  SSH: ssh -p {port} root@{ip}")
    print()
    print("Running training setup...")
    print()

    ssh_cmd = [
        "ssh",
        "-p", str(port),
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        f"root@{ip}",
        "bash -c 'git clone https://codeberg.org/Ronin48/SELMA.git && cd SELMA && ./scripts/train.sh --skip-merge'"
    ]

    # Run SSH with output streamed to terminal
    subprocess.run(ssh_cmd)


if __name__ == "__main__":
    if not os.getenv("RUNPOD_API_KEY"):
        print("ERROR: RUNPOD_API_KEY not set")
        print("Set it: export RUNPOD_API_KEY='your_key'")
        sys.exit(1)

    if not os.getenv("HF_TOKEN"):
        print("ERROR: HF_TOKEN not set")
        print("Set it: export HF_TOKEN='your_token'")
        sys.exit(1)

    print("============================================================")
    print("SELMA — RunPod Auto-Deploy")
    print("============================================================")
    print()

    # Validate template and image before proceeding
    validate_template_and_image()

    hf_token = os.getenv("HF_TOKEN")
    pod_id, ip, port = deploy_pod(hf_token)
    ssh_into_pod(ip, port)