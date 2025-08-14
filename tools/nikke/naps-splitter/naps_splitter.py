import os
import sys
import shutil
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from utils import multiprocessing as mp_utils

script_dir = Path(__file__).parent
windows_user = os.environ.get("USERNAME") or os.getlogin()

source_naps_path = Path(
    fr"C:\Users\{windows_user}\AppData\LocalLow\Unity\com_proximabeta_NIKKE\naps"
)
dest_naps_path = script_dir / "naps"
bat_file = script_dir / "naps-splitter-launcher.bat"
nau_target_path = script_dir.parent / "NAU"

def _copy_one(src: Path, dst: Path):
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return (src, None)
    except Exception as e:
        return (src, str(e))

def copytree_with_log_multithread(src: Path, dst: Path):
    jobs = []
    for root, _, files in os.walk(src):
        root_p = Path(root)
        rel = root_p.relative_to(src)
        dest_dir = dst / rel
        for name in files:
            jobs.append((root_p / name, dest_dir / name))

    if not jobs:
        print(f"[WARN] No files to copy from {src}")
        return

    cfg = mp_utils.read_config()
    n = max(1, int(cfg.get("num_processes", 1)))
    max_workers = min(32, n * 2)

    print(f"[INFO] Copying {len(jobs)} files with {max_workers} threads...")
    errors = 0

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(_copy_one, s, d): (s, d) for (s, d) in jobs}
        for fut in as_completed(futs):
            s, d = futs[fut]
            try:
                _, err = fut.result()
                if err is None:
                    print(f"[INFO] {s} → {d}")
                else:
                    errors += 1
                    print(f"[WARN] Failed {s} → {d}: {err}")
            except Exception as e:
                errors += 1
                print(f"[WARN] Exception copying {s} → {d}: {e}")

    if errors:
        print(f"[WARN] Completed with {errors} errors.")
    else:
        print("[INFO] Copy complete with no errors.")

if not source_naps_path.exists():
    print(f"[ERROR] Source naps folder not found:\n{source_naps_path}")
    raise SystemExit(1)

if dest_naps_path.exists():
    print(f"[INFO] Deleting old naps folder at {dest_naps_path}...")
    shutil.rmtree(dest_naps_path)

print(f"[INFO] Copying naps folder from:\n{source_naps_path}\n→ to:\n{dest_naps_path}")
copytree_with_log_multithread(source_naps_path, dest_naps_path)

if not bat_file.exists():
    print(f"[ERROR] .bat file not found at:\n{bat_file}")
    raise SystemExit(1)

print(f"[INFO] Running {bat_file.name} with naps folder...")
subprocess.run(
    [str(bat_file), str(dest_naps_path)],
    shell=True,
    cwd=bat_file.parent
)

if dest_naps_path.exists():
    print(f"[INFO] Deleting temporary naps folder at {dest_naps_path}...")
    shutil.rmtree(dest_naps_path)

aeb_folder = script_dir / "aeb"
if aeb_folder.exists():
    nau_target_path.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Moving aeb folder to {nau_target_path}...")
    if (nau_target_path / "aeb").exists():
        shutil.rmtree(nau_target_path / "aeb")
    shutil.move(str(aeb_folder), str(nau_target_path))
else:
    print("[ERROR] No aeb folder found — nothing to move.")

print("[DONE] All done!")
