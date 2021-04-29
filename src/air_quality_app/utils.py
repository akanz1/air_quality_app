from pathlib import Path

ROOT = Path(__file__).parents[2]


export_dir = ROOT / "data" / "export"
Path(export_dir).mkdir(parents=True, exist_ok=True)
