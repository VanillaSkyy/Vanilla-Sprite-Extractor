import os
import zipfile
from pathlib import Path
import UnityPy
import shutil
import time
from datetime import datetime
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from utils import multiprocessing as mp_utils

def hide_folder_windows(path: Path):
    if os.name == 'nt' and path.exists():
        subprocess.run(['attrib', '+h', str(path)], shell=True)

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)
CONFIG_FILE = PROJECT_ROOT / "config.txt"

def get_settings_path():
    if CONFIG_FILE.is_file():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                key, sep, value = line.partition("=")
                if key.strip() == "lost_sword_path" and value.strip():
                    return Path(value.strip())
    
    path_str = input("Enter path to Lost Sword asset folder: ").strip()
    path = Path(path_str)

    try:
        lines = []
        if CONFIG_FILE.is_file():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()

        lines = [line for line in lines if not line.lstrip().startswith("lost_sword_path")]
        lines.append(f"lost_sword_path = {path}\n")

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"[INFO] Saved lost_sword_path to {CONFIG_FILE}")
    except Exception as e:
        print(f"[WARNING] Failed to save config: {e}")
    
    return path

def run(output_folder: Path):
    now = datetime.now()
    log_file = LOGS_DIR / f"lost_sword_{now.strftime('%H-%M-%S_%d-%m-%Y')}.txt"

    def log(*args, **kwargs):
        print(*args, **kwargs)
        with open(log_file, "a", encoding="utf-8") as f:
            print(*args, **kwargs, file=f)

    input_path = get_settings_path()

    if not input_path.exists() or input_path.suffix.lower() != ".xapk":
        log(f"[ERROR] You must provide a valid .xapk file. Got: {input_path}")
        return

    temp_dir = None
    asset_files = []

    try:
        log("[INFO] Extracting XAPK...")

        temp_base = PROJECT_ROOT / "temp"
        temp_base.mkdir(exist_ok=True)

        temp_dir = temp_base / f"temp_lostsword_xapk_{now.strftime('%H-%M-%S_%d-%m-%Y')}"
        temp_dir.mkdir(exist_ok=True)
        hide_folder_windows(temp_base)

        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        apk_files = list(temp_dir.rglob("*.apk"))
        if not apk_files:
            log("[ERROR] No APK files found inside the XAPK.")
            return

        apk_extract_dir = temp_dir / "apk_contents"
        apk_extract_dir.mkdir(exist_ok=True)
        for apk in apk_files:
            log(f"[INFO] Extracting {apk.name}...")
            with zipfile.ZipFile(apk, 'r') as apk_zip:
                apk_zip.extractall(apk_extract_dir)

        asset_files = [f for f in apk_extract_dir.rglob("*") if f.is_file()]

        if not asset_files:
            log("[ERROR] No files found inside the APKs.")
            return

        log(f"[INFO] Saving to: {output_folder}")

        config = mp_utils.read_config()
        num_processes = config.get("num_processes", 1)

        count = extract_textures(asset_files, output_folder, log, num_processes)
        log(f"[DONE] Extraction complete. Extracted {count} textures to '{output_folder}'.")

    finally:
        if temp_dir and temp_dir.exists():
            safe_rmtree(temp_dir, log)


def safe_rmtree(path, log, retries=5):
    for i in range(retries):
        try:
            shutil.rmtree(path)
            log(f"[INFO] Deleted temporary folder: {path}")
            return
        except PermissionError:
            time.sleep(0.5)
    log(f"[WARN] Could not delete temp folder: {path}")


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


def process_asset_file(asset_file, output_root, root_folder):
    count = 0
    logs = []

    try:
        with open(asset_file, "rb") as f:
            env = UnityPy.load(f.read())
    except Exception as e:
        logs.append(f"[WARN] Failed to load {asset_file}: {e}")
        return count, logs

    for obj in env.objects:
        if obj.type.name == "Texture2D":
            try:
                data = obj.read()
                img = data.image
                if img is None:
                    continue

                name = get_texture_name(data, obj) or f"texture_{obj.path_id}"
                name = "".join(c if c not in '<>:"/\\|?*' else "_" for c in name)

                relative_path = os.path.relpath(asset_file, root_folder)
                if relative_path.startswith("..") or relative_path.startswith("/") or ":" in relative_path:
                    relative_path = os.path.basename(asset_file)
                relative_dir = os.path.dirname(relative_path)
                out_folder = os.path.join(output_root, relative_dir)
                os.makedirs(out_folder, exist_ok=True)

                base_name = name
                img_path = os.path.join(out_folder, f"{base_name}.png")
                counter = 1
                while os.path.exists(img_path):
                    img_path = os.path.join(out_folder, f"{base_name}_{counter}.png")
                    counter += 1

                img.save(img_path)
                count += 1
                logs.append(f"[INFO] Extracted Texture2D '{name}' to {img_path}")

            except Exception as e:
                logs.append(f"[WARN] Failed to extract Texture2D in {asset_file} obj {obj.path_id}: {e}")

    return count, logs


def extract_textures(asset_files, output_root, log, num_processes=1):
    count = 0
    root_folder = os.path.commonpath(asset_files)

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = {executor.submit(process_asset_file, f, output_root, root_folder): f for f in asset_files}

        for future in as_completed(futures):
            try:
                file_count, file_logs = future.result()
                count += file_count
                for l in file_logs:
                    log(l)
            except Exception as e:
                log(f"[ERROR] Failed processing {futures[future]}: {e}")

    return count
