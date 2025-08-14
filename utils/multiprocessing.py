import os
from pathlib import Path
import multiprocessing

CONFIG_FILE = Path(__file__).parent.parent / "config.txt"

def read_config():
    config = {"num_processes": 1}
    if not CONFIG_FILE.exists():
        return config

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = map(str.strip, line.split("=", 1))
                if key == "num_processes":
                    try:
                        n = int(value)
                        if n < 0:
                            n = 1
                        elif n == 0:
                            n = multiprocessing.cpu_count()
                        config[key] = n
                    except ValueError:
                        pass
    return config
