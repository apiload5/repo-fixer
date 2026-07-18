# 🤖 Repo-Fixer: Automated Self-Healing CLI Engine

**Repo-Fixer** ek intelligent, interactive Terminal-based (CLI) utility hai jo aapke full-stack source codebases (Next.js, Laravel, Django, Python, etc.) ko dynamically audit karti hai, bugs aur syntax errors ko trace karti hai, aur AI engines (Gemini, ChatGPT, DeepSeek) ka istemal karke unhe automatically local disk par repair karti hai. 

Yeh tool khaas tor par **Termux (Android mobile shell)** aur lightweight setups ke liye optimize kiya gaya hai bina kisi heavy local machine framework dependency ke.

---

## 🔥 Features & Production Safeguards

* **📦 Fully Interactive CLI:** Run hote hi pichli repository workspace path ka option poochta hai. Single-key click se continuous operation.
* **📥 Native Git & SSH Automation:** Script background me automatically up-to-date changes fetch (`git pull`) karti hai aur repair ke baad target remote branch par push karti hai.
* **🛡️ Command Injection Shield:** Pure list-arrays processing (`shell=False`) ke sath built hai, jisse Termux system environments me zero shell manipulation risks hote hain.
* **🔄 Safe Rollback Checkpoint:** AI injection se pehle local snapshot commit create hota hai. Agar AI response parse error de ya aap preview dekh kar push karne se mana (`n`) kar dein, to code seconds me wapas purani state me restore ho jata hai.
* **🔍 Live Git Diff Preview:** Remote GitHub repository par changes push karne se pehle aapko code modifications ka mukammal preview dikhaya jata hai.
* **⏳ Token Quota Persistence:** Daily usage data `tokens_state.json` me maintain rehta hai jo naya din shuru hote hi auto-reset ho jata hai taake continuous optimization targets complete ho sakein.

---

## 🛠️ Installation & Setup (Termux / Linux)

### 1. Requirements Setup
Termux ya apne normal Linux terminal me core packages aur environments install karein:

```bash
pkg update && pkg install python git -y
pip install google-genai openai
