import subprocess
from pathlib import Path

script_path = Path("silverjolteon-loader/MHP2-Custom-Quest-Loader/generate.py")
subprocess.run(
    ["python", script_path.name],
    cwd=script_path.parent,
    check=True
)

