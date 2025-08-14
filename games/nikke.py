import subprocess
import sys
from pathlib import Path
import shutil
import UnityPy
import os
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from utils import multiprocessing as mp_utils

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def run_script(script_path, log):
    log(f"\n=== Running {script_path.name} ===")
    result = subprocess.run([sys.executable, str(script_path)])
    if result.returncode != 0:
        log(f"[ERROR] Script {script_path.name} exited with code {result.returncode}. Stopping.")
        sys.exit(result.returncode)
    log(f"=== Finished {script_path.name} ===\n")

def run(output_folder: Path):
    now = datetime.now()
    log_file = LOGS_DIR / f"nikke_{now.strftime('%H-%M-%S_%d-%m-%Y')}.txt"

    def log(*args, **kwargs):
        print(*args, **kwargs)
        with open(log_file, "a", encoding="utf-8") as f:
            print(*args, **kwargs, file=f)

    base_dir = Path(__file__).parent.parent

    scripts = [
        base_dir / "tools" / "nikke" / "naps-splitter" / "naps_splitter.py",
        base_dir / "tools" / "nikke" / "NAU" / "key_generator.py",
        base_dir / "tools" / "nikke" / "NAU" / "final_decrypt.py",
    ]

    for script in scripts:
        if not script.exists():
            log(f"[ERROR] Script not found: {script}")
            sys.exit(1)
        run_script(script, log)

    log("All scripts completed successfully! Ready for Texture2D extraction.")

    decrypted_folder = base_dir / "tools" / "nikke" / "NAU" / "Decrypted"
    if not decrypted_folder.exists():
        log(f"[ERROR] Decrypted folder not found: {decrypted_folder}")
        sys.exit(1)

    asset_files = list(decrypted_folder.rglob("*"))
    asset_files = [f for f in asset_files if f.is_file()]

    count = extract_textures(asset_files, output_folder, log)
    log(f"[DONE] Extraction complete. Extracted {count} textures to '{output_folder}'.")

    try:
        shutil.rmtree(decrypted_folder)
        log(f"[INFO] Deleted Decrypted folder: {decrypted_folder}")
    except Exception as e:
        log(f"[ERROR] Failed to delete Decrypted folder: {e}")


def get_texture_name(data, obj):
    try:
        tree = data.read_typetree()
    except Exception:
        tree = {}

    if isinstance(tree, dict):
        for key in ["m_Name", "name"]:
            if key in tree and tree[key]:
                return tree[key]

        stream_data = tree.get("m_StreamData")
        if stream_data and isinstance(stream_data, dict):
            path = stream_data.get("m_Path")
            if path:
                return os.path.splitext(os.path.basename(path))[0]

        source = tree.get("m_Source")
        if source and isinstance(source, dict):
            source_name = source.get("name")
            if source_name:
                return source_name

    if hasattr(data, "m_Name") and data.m_Name:
        return data.m_Name
    if hasattr(data, "name") and data.name:
        return data.name

    return str(obj.path_id)


def _process_asset_file(asset_file, output_root, root_folder):
    count = 0
    logs = []
    try:
        env = UnityPy.load(str(asset_file))
        for obj in env.objects:
            if obj.type.name == "Texture2D":
                try:
                    data = obj.read()
                    img = data.image
                    if img is None:
                        continue

                    name = get_texture_name(data, obj)
                    name = name.strip() or f"texture_{obj.path_id}"
                    for ch in '<>:"/\\|?*':
                        name = name.replace(ch, "_")

                    relative_path = os.path.relpath(asset_file, root_folder)
                    relative_dir = os.path.dirname(relative_path)
                    out_folder = os.path.join(output_root, relative_dir)
                    os.makedirs(out_folder, exist_ok=True)

                    base_name = name
                    img_path = os.path.join(out_folder, f"{base_name}.png")
                    counter = 1
                    while os.path.exists(img_path):
                        img_path = os.path.join(out_folder, f"{base_name}_{counter}.png")
                        counter += 1

                    if not os.path.abspath(img_path).startswith(os.path.abspath(output_root)):
                        logs.append(f"[ERROR] Invalid save path generated: {img_path}")
                        continue

                    img.save(img_path)
                    count += 1
                    logs.append(f"[INFO] Extracted Texture2D '{name}' to {img_path}")

                except Exception as e:
                    logs.append(f"[WARN] Failed to extract Texture2D in {asset_file} obj {obj.path_id}: {e}")
    except Exception as e:
        logs.append(f"[ERROR] Failed to process file {asset_file}: {e}")

    return count, logs


def extract_textures(asset_files, output_root, log):
    root_folder = os.path.commonpath(asset_files)
    cfg = mp_utils.read_config()
    n = max(1, int(cfg.get("num_processes", 1)))

    log(f"[INFO] Extracting textures using {n} processes...")
    count = 0

    with ProcessPoolExecutor(max_workers=n if n > 0 else None) as executor:
        futures = {executor.submit(_process_asset_file, af, output_root, root_folder): af for af in asset_files}
        for fut in as_completed(futures):
            c, logs_list = fut.result()
            count += c
            for line in logs_list:
                log(line)

    return count
