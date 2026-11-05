# Nested notebook execution contract

All project notebooks are launched from the repository root with the explicitly selected `portfolio` kernel. At the start of each notebook, run this bootstrap before importing project modules:

```python
from pathlib import Path
import sys

def find_project_root(start=Path.cwd()):
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / "PRD.md").is_file() and (candidate / "src").is_dir():
            return candidate
    raise FileNotFoundError("Run this notebook from inside the portfolio project.")

PROJECT_ROOT = find_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
```

The notebook then imports shared logic from `src`. Read/write paths derive from `PROJECT_ROOT`, never the machine's current drive or an absolute user path. The clean environment, registered local kernel, and a minimal nested notebook still need execution verification before S1 can close.
