from pathlib import Path

import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
notebook = nbformat.read(root / "notebooks/01_reproducible_evaluation.ipynb", as_version=4)
NotebookClient(
    notebook, timeout=180, kernel_name="python3", resources={"metadata": {"path": str(root)}}
).execute()
(root / "var").mkdir(exist_ok=True)
nbformat.write(notebook, root / "var/executed-evaluation.ipynb")
print("Notebook executed: training, holdout report and direct/API equality passed")
