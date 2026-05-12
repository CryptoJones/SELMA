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
    req = Request(RUNPOD_API, data=data, headers={
        "Content-Type": "application/json",
        "api-key": api_key,
    })

    try:
        with urlopen(req) as resp:
            result = json.loads(resp.read())
            if "errors" in result:
                raise Exception(f"API error: {result['errors']}")
            return result.get("data", {})
    except HTTPError as e:
        raise Exception(f"HTTP {e.code}: {e.read().decode()}")

def deploy_pod(hf_token):
    """Deploy A100 pod with HF_TOKEN."""
    # List available GPUs to find A100
    gpu_query = """
    query {
      gpuTypes {
        id
        displayName
      }
    }
    """
    result = call_api(gpu_query)
    gpu_id = None
    for gpu in result.get("gpuTypes", []):
        if "A100" in gpu.get("displayName", ""):
            gpu_id = gpu["id"]
            break

    if not gpu_id:
        print("No A100 GPU found. Available GPUs:")
        for gpu in result.get("gpuTypes", []):
            print(f"  {gpu['displayName']}")
        sys.exit(1)

    # Deploy pod
    deploy_query = """
    mutation podFindAndDeployOnDemand($input: PodFindAndDeployOnDemandInput!) {
      podFindAndDeployOnDemand(input: $input) {
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

    variables = {
        "input": {
            "name": "SELMA-Training",
            "gpuTypeId": gpu_id,
            "gpuCount": 1,
            "volumeInGb": 100,
            "containerDiskInGb": 50,
            "templateId": "runpod-pytorch",
            "imageName": "runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04",
            "env": [
                {"key": "HF_TOKEN", "value": hf_token}
            ],
            "ports": "22/tcp",
        }
    }

    print("Deploying A100-80GB pod...")
    result = call_api(deploy_query, variables)
    pod = result.get("podFindAndDeployOnDemand", {})

    if not pod.get("id"):
        print(f"Failed to deploy: {pod}")
        sys.exit(1)

    pod_id = pod["id"]
    print(f"✓ Pod created: {pod_id}")
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
            status
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

        if pod_status.get("status") == "RUNNING":
            ports = pod_status.get("runtime", {}).get("ports", [])
            if ports and ports[0].get("publicPort"):
                return pod_id, ports[0]["ip"], ports[0]["publicPort"]

        print(f"  {attempt+1}/60 - Status: {pod_status.get('status', 'unknown')}")

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

    hf_token = os.getenv("HF_TOKEN")
    pod_id, ip, port = deploy_pod(hf_token)
    ssh_into_pod(ip, port)
