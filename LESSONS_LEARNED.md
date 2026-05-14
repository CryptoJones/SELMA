# Lessons Learned — SELMA Training

This document captures dependency conflicts, environment bugs, and hard-won fixes
encountered during SELMA training runs. Read this before you start.

For issues common to all Ronin 48 models (RunPod environment, bitsandbytes, torchvision,
QLoRA dependency conflicts), see [ABBY's LESSONS_LEARNED.md](https://codeberg.org/Ronin48/ABBY/raw/branch/main/LESSONS_LEARNED.md) —
it has the most complete record of the first training run.

---

## SELMA-Specific Notes

### Training Monitor Missed a Disk-Full Crash

The training monitor has a known failure mode: if the pod crashes before GPU ever activates
(e.g. disk full during model download, bad import, OOM before first forward pass), the monitor
reports `GPU 0% | active=False` and interprets this as "still initializing." It does not alert.

This happened at least three times across Ronin 48 training runs before the monitor was fixed
with pre-flight checks and a stuck-pod alert.

See [ABBY Error #20](https://codeberg.org/Ronin48/ABBY/raw/branch/main/LESSONS_LEARNED.md)
for the full incident writeup, root causes, and fixes applied.

**Rule: `GPU 0% | active=False` after 20+ minutes = crashed. SSH in and check `/workspace/logs/train.log`.**

---

## Contributing

If you hit a new error and fix it, please add it here. The people walking behind
you will thank you.
