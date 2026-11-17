# ASDE Full Recovery Package

Checkpoint: 20261117T095538Z

## Files
- `research_state.json` at checkpoint root: serialized runtime state.
- `artifacts/`: discovered research reports and outputs.
- `recovery_package/ADSE_MASTER_RECOVERY.ipynb`: notebook source.
- `recovery_package/source/`: deduplicated source files.
- `recovery_package/recovery_manifest.json`: source and artifact inventory.

## Restore in a fresh Colab

1. Clone/download the ASDE GitHub repository.
2. Open `checkpoints/colab_runtime/20261117T095538Z/recovery_package/ADSE_MASTER_RECOVERY.ipynb`.
3. Configure secrets separately through Colab Secrets.
4. Load `research_state.json` for inspection:

```python
import json
from pathlib import Path

p = Path("checkpoints/colab_runtime/20261117T095538Z/research_state.json")
with p.open(encoding="utf-8") as f:
    recovered_state = json.load(f)

print(len(recovered_state), list(recovered_state)[:50])
```

5. Re-run initialization cells to recreate engines, clients and runtime objects.

Notebook outputs were removed from the recovery copy. Non-finite values in
the state are preserved as explicit marker strings, not numerical values.
No credentials are included.
