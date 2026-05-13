# Ronin 48 QLoRA Training Environment
#
# Based on a stable PyTorch + CUDA 12.1 image. Bakes in all dependency
# fixes discovered during ABBY/SELMA/BONES/BRUNO training runs so that
# anyone spinning up a pod doesn't have to fight the environment.
#
# Build:
#   docker build -t ronin48/qlora-training:latest .
#   docker push ronin48/qlora-training:latest
#
# RunPod: use this image when creating a custom template.
# Container disk: 50GB | Network volume: 300GB (model weights ~130GB)

FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

# torchvision ships pre-built for specific torch versions and crashes on mismatch.
# We do text-only training — no vision needed.
RUN pip uninstall -y torchvision torchaudio 2>/dev/null || true

# Install pinned-to-stable training stack
RUN pip install --no-cache-dir \
    "transformers>=4.46.0" \
    "peft>=0.13.0" \
    "trl>=0.12.0" \
    "bitsandbytes>=0.44.0" \
    "accelerate>=1.0.0" \
    "datasets" \
    "pyyaml" \
    "requests" \
    "tqdm" \
    "rich"

# SSH setup (RunPod standard)
RUN apt-get update -qq && apt-get install -y -q openssh-server && \
    ssh-keygen -A && \
    mkdir -p /run/sshd && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

# HuggingFace cache always goes to the network volume
ENV HF_HOME=/workspace/hf_cache

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
