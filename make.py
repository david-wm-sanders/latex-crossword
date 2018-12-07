import subprocess
import sys
from pathlib import Path

texf = Path(sys.argv[1]).resolve()
p = Path(__file__).parent
print(f"Running make.py on {texf}")
command = ["pdflatex.exe", str(texf)]
subprocess.run(command)
print("Cleaning up...")
Path(f"{texf.parent}/{texf.stem}.aux").unlink()
Path(f"{texf.parent}/{texf.stem}.log").unlink()
Path(f"{texf.parent}/{texf.stem}.out").unlink()
