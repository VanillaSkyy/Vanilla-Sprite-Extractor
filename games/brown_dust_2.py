from pathlib import Path
import UnityPy
import os
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from utils import multiprocessing as mp_utils

UnityPy.config.FALLBACK_UNITY_VERSION = "2022.3.15f1"

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
                if key.strip() == "bd2_path" and value.strip():
                    return Path(value.strip())
    
    path_str = input("Enter path to Brown Dust 2 asset folder: ").strip()
    path = Path(path_str)

    try:
        lines = []
        if CONFIG_FILE.is_file():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()

        lines = [line for line in lines if not line.lstrip().startswith("bd2_path")]
        lines.append(f"bd2_path = {path}\n")

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"[INFO] Saved bd2_path to {CONFIG_FILE}")
    except Exception as e:
        print(f"[WARNING] Failed to save config: {e}")
    
    return path

def run(output_folder: Path):
    now = datetime.now()
    log_file = LOGS_DIR / f"brown_dust_2_{now.strftime('%H-%M-%S_%d-%m-%Y')}.txt"

    def log(*args, **kwargs):
        print(*args, **kwargs)
        with open(log_file, "a", encoding="utf-8") as f:
            print(*args, **kwargs, file=f)

    input_folder = get_settings_path()

    if not input_folder.exists() or not input_folder.is_dir():
        log(f"[ERROR] Input folder not found: {input_folder}")
        return

    log(f"[INFO] Extracting from: {input_folder}")
    log(f"[INFO] Saving to: {output_folder}")

    asset_files = [f for f in input_folder.rglob("*") if f.is_file()]

    if not asset_files:
        log("[ERROR] No files found in input folder.")
        return

    count = extract_textures(asset_files, output_folder, log)
    log(f"[DONE] Extraction complete. Extracted {count} textures to '{output_folder}'.")


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
        env = UnityPy.load(str(asset_file))
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
                logs.append(f"[WARN] Failed Texture2D in {asset_file} obj {obj.path_id}: {e}")

    return count, logs


def extract_textures(asset_files, output_root, log):
    count = 0
    root_folder = os.path.commonpath(asset_files)

    config = mp_utils.read_config()
    num_processes = config.get("num_processes", 1)

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
