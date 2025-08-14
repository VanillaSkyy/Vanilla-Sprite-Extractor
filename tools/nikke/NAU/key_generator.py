import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.txt"

def get_settings_path():
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
    CONFIG_FILE = PROJECT_ROOT / "config.txt"

    if CONFIG_FILE.is_file():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                key, sep, value = line.partition("=")
                if key.strip() == "nikke_settings_json_path" and value.strip():
                    return Path(value.strip())

    path_str = input(
        "Enter full path to settings.json (e.g. D:/Nikke/NIKKE/game/nikke_Data/StreamingAssets/aa/settings.json): "
    ).strip()
    path = Path(path_str)

    try:
        lines = []
        if CONFIG_FILE.is_file():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()

        lines = [line for line in lines if not line.lstrip().startswith("nikke_settings_json_path")]
        lines.append(f"nikke_settings_json_path = {path}\n")

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"[INFO] Saved settings path to {CONFIG_FILE}")
    except Exception as e:
        print(f"[WARNING] Failed to save config: {e}")

    return path


def main():
    settings_path = get_settings_path()

    if not settings_path.is_file():
        print(f"[ERROR] File not found: {settings_path}")
        return

    keys_dir = Path(__file__).parent.parent / "NAU" / "Keys"
    keys_dir.mkdir(parents=True, exist_ok=True)

    with open(settings_path, 'r', encoding='utf-8') as f:
        try:
            jsonData = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse JSON: {e}")
            return

    try:
        m_Data = json.loads(jsonData["m_ExtraInitializationData"][0]["m_Data"])
        keySets = m_Data["KeySets"]
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"[ERROR] Error reading keys from JSON structure: {e}")
        return

    for set_ in keySets:
        version_dir = keys_dir / f"v{set_['version']}"
        version_dir.mkdir(parents=True, exist_ok=True)

        for key_index, byte_array in enumerate(set_["keys"]):
            byte_values = byte_array["Bytes"]
            data = bytes(byte_values)

            key_file = version_dir / f"key_{key_index}"
            try:
                with open(key_file, "wb") as kf:
                    kf.write(data)
                print(f"[DONE] Successfully wrote key v{set_['version']}/key_{key_index}")
            except Exception as e:
                print(f"[ERROR] ERROR writing {key_file}: {e}")

if __name__ == "__main__":
    main()
