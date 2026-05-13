# Training on RunPod

**Estimated cost: ~$12–15 per model (70B, A100 PCIe at $1.39/hr)**
**Estimated time: 8–10 hours on a single A100-80GB**

This guide covers the Ronin 48 training process for SELMA, ABBY, BONES, and BRUNO on RunPod.

---

## What You Need

1. A RunPod account with at least $40 in credits (buffer for the full first responder suite)
2. A HuggingFace account with the Llama 3.3 license accepted:
   `https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct`
3. Your HuggingFace token (Settings → Access Tokens → New token, read-only is fine)

---

## Step 1 — Deploy a Pod

### Option A: Via the monitor script (recommended for queue runs)

```bash
python3 scripts/runpod_monitor.py
```

This deploys an A100 pod with the correct volume size and env vars, then monitors
GPU activity and auto-queues the next model when training completes.

**Important:** The script checks for running pods before deploying. Never run it
if a pod is already active — it will abort safely, but double-check first.

### Option B: Manual (RunPod web console)

1. Go to `https://www.runpod.io/console/pods` and click **Deploy**
2. Select GPU: **NVIDIA A100 80GB PCIe** (~$1.39/hr)
3. Select template: **RunPod PyTorch 2.2** (has CUDA pre-installed)
4. Set storage: **200GB network volume** (model weights are ~130GB)
5. Container disk: **50GB**
6. Under **Environment Variables**, add:
   - `HF_TOKEN` = your HuggingFace token
   - `HF_HOME` = `/workspace/hf_cache`
   - `TRANSFORMERS_CACHE` = `/workspace/hf_cache`
7. Click **Deploy On-Demand**

---

## Step 2 — Start Training

> **Note:** SSH is unreliable on RunPod templates — the template's `start.sh` runs
> `sleep infinity` rather than launching sshd. Use the **web terminal** instead.

1. In the RunPod console, click **Connect** on your pod
2. Choose **Web Terminal**
3. Paste the launch command for your model:

**SELMA:**
```bash
HF_TOKEN=your_token_here bash <(curl -s https://codeberg.org/Ronin48/SELMA/raw/branch/main/scripts/launch.sh)
```

**ABBY:**
```bash
HF_TOKEN=your_token_here bash <(curl -s https://codeberg.org/Ronin48/ABBY/raw/branch/main/scripts/launch.sh)
```

**BONES:**
```bash
HF_TOKEN=your_token_here bash <(curl -s https://codeberg.org/Ronin48/BONES/raw/branch/main/scripts/launch.sh)
```

**BRUNO:**
```bash
HF_TOKEN=your_token_here bash <(curl -s https://codeberg.org/Ronin48/BRUNO/raw/branch/main/scripts/launch.sh)
```

The script handles everything: clone, pip install, data generation, and training.
Watch for `[train] starting QLoRA training...` — after that the GPU should spike above 10%.

### What launch.sh does

1. Sets `HF_HOME` to `/workspace/hf_cache` (200GB volume — never the container disk)
2. Clones or updates the repo into `/workspace/<MODEL>`
3. Upgrades pip and installs all dependencies
4. Runs synthetic data generation
5. Prepares the training dataset
6. Starts `train_qlora.py`

---

## Step 3 — Monitor Training

Training is monitored automatically by `runpod_monitor.py` when running a queue.
For a standalone pod, you can watch GPU activity in the RunPod console or check logs:

```bash
tail -f /workspace/logs/train.log
```

GPU utilization above 10% = training is active.
GPU dropping back to 0% after being active = training complete.

---

## Step 4 — Save the Adapter

**Do this before stopping the pod.**

Upload to HuggingFace:

```bash
huggingface-cli upload Ronin48/selma-lora-adapter /workspace/SELMA/output/selma-qlora/final/
```

---

## Step 5 — Terminate the Pod

**You are billed until the pod is terminated.** Terminate immediately after the upload.

In the RunPod console: **Manage → Terminate**

Or via the monitor script — it terminates automatically when GPU goes idle.

---

## Cost Breakdown (Single Model, A100 PCIe)

| Item | Hours | Rate | Cost |
|---|---|---|---|
| Model weight download | ~1 hr | ~$1.39/hr | ~$1.40 |
| Training | ~8–9 hrs | ~$1.39/hr | ~$11–12 |
| Buffer | — | — | ~$2 |
| **Total** | | | **~$14–16** |

Full first responder suite (ABBY + SELMA + BONES + BRUNO): ~$55–65

---

## Troubleshooting

**Out of disk space during download:**
Model weights must go to `/workspace/hf_cache`, not the container disk.
`launch.sh` sets this automatically. If you're running manually, ensure:
```bash
export HF_HOME=/workspace/hf_cache
export TRANSFORMERS_CACHE=/workspace/hf_cache
```

**Out of memory during training:**
Reduce `per_device_train_batch_size` in `configs/training_config.yaml` from 2 to 1.

**HuggingFace download failing:**
Confirm `HF_TOKEN` is set and you accepted the Llama 3.3 license at HuggingFace.

**Pod terminated unexpectedly:**
Use On-Demand, not Spot, for long training runs.

**SSH connection refused:**
Use the web terminal instead (Connect → Web Terminal in RunPod console).
The template's startup script does not launch sshd.
