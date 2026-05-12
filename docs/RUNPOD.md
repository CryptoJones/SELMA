# Training SELMA on RunPod

**Estimated cost: ~$25–35 for one state model (70B)**
**Estimated time: 8–10 hours on a single A100-80GB**

## What You Need Before Starting

1. A RunPod account funded with at least $40 (leaves buffer for retries)
2. A HuggingFace account with the Llama 3.1 license accepted:
   https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct
3. Your HuggingFace token (Settings → Access Tokens → New token, read-only is fine)
4. Your RunPod API key (RunPod console → Settings → API Keys)

---

## Step 1 — Launch a Pod

### Option A: Fully Automated (For the Lazy™) — ⚠️ NOT RECOMMENDED FOR SECURITY REASONS

Because programmers are fundamentally lazy — and that's a feature, not a bug — we built a script that does everything:

⚠️ **Security warning:** This script runs unattended SSH commands on a remote pod. Your API keys are passed as environment variables. Only use this on trusted machines or in isolated environments.

```bash
export RUNPOD_API_KEY="your_runpod_key_here"
export HF_TOKEN="hf_your_token_here"
python3 scripts/runpod_deploy.py
```

This script:
1. Deploys an A100-80GB pod to RunPod
2. Waits for it to be ready (~2-3 minutes)
3. SSHes in automatically
4. Clones SELMA and starts training
5. Streams output to your terminal

No web console. No clicking. No thinking. Just training.

### Option B: Step-by-Step Configurator

If you prefer to see the steps before running them:

```bash
export RUNPOD_API_KEY="your_runpod_key_here"
export HF_TOKEN="hf_your_token_here"
bash scripts/launch_runpod_manual.sh
```

The script validates your setup and prints exact web console instructions with your HF_TOKEN pre-filled.

### Option C: Manual (RunPod web console)

1. Go to https://www.runpod.io/console/pods and click **Deploy**
2. Select GPU: **NVIDIA A100 80GB PCIe** (~$2–3/hr) or **SXM** (~$3–4/hr)
   - PCIe is cheaper and sufficient; SXM is faster but costs more
3. Select template: **RunPod PyTorch 2.1** (has CUDA 11.8 pre-installed)
4. Set storage: **100GB volume** (model weights alone are ~140GB during training)
5. Under **Environment Variables**, add:
   - `HF_TOKEN` = your HuggingFace token
6. Click **Deploy On-Demand**

---

## Step 2 — SSH Into the Pod

Once the pod shows **Running** in the console, click **Connect** and copy the SSH command. It will look like:

```bash
ssh root@<ip> -p <port> -i ~/.ssh/id_rsa
```

---

## Step 3 — Run Training

Once connected via SSH:

```bash
# Clone the repo
git clone https://codeberg.org/Ronin48/SELMA.git
cd SELMA

# Run the full pipeline (data collection → training → adapter save)
# Skip the merge step — see note below
chmod +x scripts/train.sh
./scripts/train.sh --skip-merge
```

Training will print loss every 10 steps. Expect ~8–10 hours. You can safely
close your SSH session — the pod keeps running. Reconnect anytime to check progress:

```bash
tail -f output/selma-qlora/trainer_log.jsonl
```

---

## Step 4 — Save Your Work Before Stopping the Pod

**Do this before you stop the pod or your adapter will be lost.**

Upload the adapter to HuggingFace:

```bash
huggingface-cli upload <your-username>/selma-70b-georgia-adapter \
    output/selma-qlora/final/
```

Or copy it locally over SCP:

```bash
# Run this on your local machine (not the pod)
scp -P <port> -r root@<ip>:~/SELMA/output/selma-qlora/final/ ./selma-adapter/
```

---

## Step 5 — Stop the Pod

**Stop the pod as soon as the upload/copy finishes — you're billed until you stop it.**

In the RunPod console, click the **Stop** button on your pod.
Or via the API:

```bash
runpodctl stop pod <pod-id>
```

---

## About the Merge Step

Merging the LoRA adapter into the 70B base model requires loading ~140GB into
CPU RAM. RunPod A100 pods typically have 58–120GB of system RAM, which is not
enough. **Skip the merge on RunPod** — the adapter works perfectly without it:

- To serve with Ollama: load base model + adapter together (vLLM supports this)
- To submit to SELMA: just upload the adapter to HuggingFace and open a PR
- To do the merge: use a high-memory CPU instance (AWS `r6i.4xlarge`, ~$1/hr,
  ~140GB RAM) and run `python scripts/training/merge_adapter.py` there

---

## Cost Breakdown (One State Model, A100-80GB PCIe)

| Item | Hours | Rate | Cost |
|---|---|---|---|
| Training | ~9 hrs | ~$2.50/hr | ~$22.50 |
| Data collection + setup | ~1 hr | ~$2.50/hr | ~$2.50 |
| Buffer / retries | — | — | ~$5.00 |
| **Total** | | | **~$30** |

Spot instances can cut this in half but may be interrupted mid-training.
Use **On-Demand** for a training run to avoid losing progress.

---

## Troubleshooting

**Out of memory during training:**
Reduce `per_device_train_batch_size` in `configs/training_config.yaml` from 2 to 1.

**HuggingFace download failing:**
Make sure `HF_TOKEN` is set and you accepted the Llama 3.1 license at
https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct

**Pod terminated unexpectedly:**
Use On-Demand, not Spot, for long training runs. Check RunPod console for interruption reason.

**Training loss not decreasing:**
Check that `data/processed/train.jsonl` was created correctly by `prepare_dataset.py`.
It should have at least 10,000 examples.
