import subprocess
from pathlib import Path
import sys
import shutil

def main():
    script_dir = Path(__file__).parent
    nau_folder = script_dir

    input_folder = nau_folder / "aeb"
    output_folder = nau_folder / "Decrypted"

    if not input_folder.exists():
        print(f"[ERROR] Input folder does not exist: {input_folder}")
        return
    
    if output_folder.exists() and output_folder.is_dir():
        try:
            shutil.rmtree(output_folder)
            print(f"[INFO] Deleted existing folder: {output_folder}")
        except Exception as e:
            print(f"[ERROR] Could not delete existing folder {output_folder}: {e}")
            return

    output_folder.mkdir(exist_ok=True)

    exe_path = nau_folder / "nikkeassetunpacker.exe"
    if not exe_path.exists():
        print(f"[ERROR] Executable not found at {exe_path}")
        return

    cmd = [
        str(exe_path),
        "d",
        "-i", str(input_folder),
        "-o", str(output_folder)
    ]

    print("Running:", " ".join(cmd))

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True
    )

    proc.communicate(input="\n")

    if proc.returncode == 0 or proc.returncode == 1:
        print("[DONE] Files unpacked successfully.")
        try:
            shutil.rmtree(input_folder)
            print(f"[DONE] Deleted input folder: {input_folder}")
        except Exception as e:
            print(f"[ERROR] Could not delete {input_folder}: {e}")
    else:
        print(f"[ERROR] nikkeassetunpacker exited with code {proc.returncode}")

if __name__ == "__main__":
    main()
