# 🧠 Git Personality Profiler v2.0

> "Show me your commit history, and I'll tell you who you are."

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The **Git Personality Profiler** is a sophisticated CLI tool designed to decode the human behavior behind the code. By analyzing commit timestamps, message semantics, and code impact, it generates a unique "Developer DNA" profile and assigns one of our 6 core archetypes.

---

## 📸 Preview

```text
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃             🧠 GIT PERSONALITY PROFILER 2.0            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

📊 STATISTIEKEN
  Commits: 42
  Impact:  +12,450 / -3,120 regels
  Favoriete dag: Saturday (15 commits)

🧬 DNA PROFIEL
Nachtuil 🧛      [██████████░░░░░░░░░░]  50.0%
Vroege Vogel 🐦  [░░░░░░░░░░░░░░░░░░░░]   2.0%
Weekend Warrior ⚔️ [██████████████░░░░░░]  70.0%
Perfectionist ✨ [██████░░░░░░░░░░░░░░]  30.0%
Chaos Aap 🐒     [█░░░░░░░░░░░░░░░░░░░]   5.0%

🏆 UW ARCHETYPE:
  The Midnight Shadow 🧛
  "Leeft op cafeïne en codeert als de rest van de wereld slaapt."
```

---

## ✨ Features

- **🕒 Temporal Analysis**: Deep-dive into your peak productivity hours.
- **🧬 DNA Profiling**: Real-time bars reflecting your coding habits (Refactoring vs. Chaos).
- **💥 Impact Metrics**: Track your net contribution (Insertions vs. Deletions).
- **🎭 Archetype Engine**: Automatically classifies you into profiles like *The Architect*, *The Tank*, or *The Chaos Engineer*.
- **💢 Sentiment Heuristics**: Detects frustration levels in commit messages.

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/KippieG/git-personality-profiler.git
   cd git-personality-profiler
   ```

2. **No dependencies required!** Just pure Python 3.

## 🛠 Usage

Analyze the current directory:
```bash
python3 profiler.py
```

Analyze a specific project:
```bash
python3 profiler.py /path/to/awesome-project
```

## 🎭 The Archetypes

| Archetype | Description |
| :--- | :--- |
| **The Midnight Shadow 🧛** | High activity between 00:00 - 05:00. Powered by coffee. |
| **The Architect ✨** | High refactor-to-feature ratio. Loves clean code. |
| **The Tank 🧱** | Rare but massive commits. High impact per push. |
| **The Chaos Engineer 🐒** | Short messages (wip, fix, .). Speed over documentation. |
| **The Grumpy Dev 💢** | Sentiment analysis detected high frustration levels. |
| **The Passionate Coder ⚔️** | High weekend activity. Coding is a lifestyle. |

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---
*Developed for developers who want to know themselves better.*
