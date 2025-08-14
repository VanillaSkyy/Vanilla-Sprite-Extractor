# Vanilla's Sprite Extractor

**Vanilla’s Sprite Extractor** is a simple and fast Python tool designed to help wiki editors, database maintainers, and game enthusiasts extract sprites from Unity-based games with minimal effort.  
No unnecessary complexity — just point it to the game files, and get clean, ready-to-use sprites for your projects.

---

## ✨ Features
- 🖼 **Direct Sprite Extraction** — quickly grab sprites from Unity game files.
- ⚡ **Fast & Lightweight** — multi-threading system for faster extraction, no bloated UI, just run and get results.
- 🛠 **Straight to the Point** — minimal setup, maximum output.
- 📁 **Organized Output** — extracted sprites are neatly saved in folders.

---

## 📦 Installation

### Requirements
- **Python 3.10+**
- `pip` (comes with Python)

### Steps
1. **Install Python**  
   Download and install Python 3.10 or higher from [python.org](https://www.python.org/downloads/).

2. **Download the project**
   Clone or download this repository:
   ```bash
   git clone https://github.com/VanillaSkyy/Vanilla-Sprite-Extractor.git
   cd vanilla-sprite-extractor
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage

### Run the program
```bash
python main.py
```
Follow the on-screen instructions to select a supported game and extract its sprites.

### Config File
The program uses a `config.txt` file to store settings, such as:
- NIKKE's `settings.json` path
- Number of threads to use

---

## 📂 Output and Logs
- Extracted sprites will be saved in the `output/` folder inside the project directory.
- Logs every process in `logs/`

---

## 🎮 Supported Games
- Azur Lane
- Blue Archive
- Brown Dust 2
- Lost Sword
- Goddess of Victory: NIKKE
- Resonance Solstice
- Silver and Blood
- Starseed: Asnia Trigger
- Trickcal: Chibi Go!

---

## 📝 License
This project is licensed under the **GPL-3.0 license**. See `LICENSE` for details.

---

## 💖 Credits
- [K0lb3](https://github.com/K0lb3) for creating UnityPy
- Bingle for creating NAU and NAU Key Generator for NIKKE

Created with love by **VanillaSkyy**
