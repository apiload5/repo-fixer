*README.md - English + Urdu Both*
🤖 Repo-Fixer: Automated Self-Healing CLI Engine

**English:**  
`Repo-Fixer` is an intelligent, interactive Terminal-based (CLI) utility that dynamically audits your full-stack source codebases (Next.js, Laravel, Django, Python, etc.), traces bugs and syntax errors, and automatically repairs them on local disk using AI engines (Gemini, ChatGPT, DeepSeek).

This tool is specifically optimized for **Termux (Android mobile shell)** and lightweight setups without any heavy local machine framework dependencies.

**اردو:**  
`Repo-Fixer` ایک ذہین، انٹرایکٹو Terminal پر مبنی (CLI) یوٹیلیٹی ہے جو آپ کے Full-Stack سورس کوڈبیسز (Next.js, Laravel, Django, Python وغیرہ) کو ڈائنامکلی آڈٹ کرتی ہے، Bugs اور Syntax Errors کو ٹریس کرتی ہے، اور AI انجنز (Gemini, ChatGPT, DeepSeek) کا استعمال کرکے انہیں لوکل ڈسک پر خودکار طریقے سے Repair کر دیتی ہے۔

یہ ٹول خاص طور پر **Termux (Android Mobile Shell)** اور ہلکے پھلکے سیٹ اپس کے لیے Optimize کیا گیا ہے بغیر کسی ہیوی لوکل مشین فریم ورک Dependency کے۔

---

🔥 Features & Production Safeguards | خصوصیات اور سیفٹی

**English:**
* **📦 Fully Interactive CLI:** On launch it asks for the last repository workspace path. Continue with a single-key click.
* **📥 Native Git & SSH Automation:** Automatically `git pull` latest changes and `git push` to target remote branch after repair.
* **🛡️ Command Injection Shield:** Built with pure list-arrays processing (`shell=False`) for zero shell manipulation risks in Termux.
* **🔄 Safe Rollback Checkpoint:** Creates a local snapshot commit before AI injection. If AI fails or you reject the preview, code restores in seconds.
* **🔍 Live Git Diff Preview:** Shows a complete preview of code modifications before pushing to GitHub.
* **⏳ Token Quota Persistence:** Daily usage saved in `tokens_state.json` and auto-resets on a new day.

**اردو:**
* **📦 مکمل انٹرایکٹو CLI:** چلتے ہی پچھلی Repository کا Path پوچھتا ہے۔ ایک Key دبانے سے کام جاری۔
* **📥 نیٹو Git اور SSH آٹومیشن:** Repair کے بعد خودکار `git pull` اور `git push` کرتا ہے۔
* **🛡️ کمانڈ انجیکشن شیلڈ:** `shell=False` لسٹ ایریز پر بنی ہے۔ Termux میں 100% سیکیور ہے۔
* **🔄 سیف رول بیک چیک پوائنٹ:** AI سے پہلے Backup Commit بناتا ہے۔ اگر AI فیل ہو یا آپ `n` دبائیں تو کوڈ واپس ریسٹور۔
* **🔍 لائیو Git Diff پریویو:** GitHub پر Push سے پہلے تمام تبدیلیاں دکھاتا ہے۔
* **⏳ ٹوکن کوٹہ پرسیسٹنس:** روزانہ کا استعمال `tokens_state.json` میں محفوظ اور نیا دن شروع ہوتے ہی Auto-Reset۔

---

🛠️ Installation & Setup | انسٹالیشن

**English:**
1. Requirements Setup
Install in Termux or Linux terminal:

```bash
pkg update && pkg install python git -y
pip install google-genai openai
2. Set API Keys
export GEMINI_API_KEY="your_key"
export DEEPSEEK_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
3. Run
git clone https://github.com/apiload5/repo-fixer/
cd repo-fixer
python main.py
*اردو:*
1. ریکوائرمنٹس سیٹ اپ
Termux یا Linux Terminal میں یہ کمانڈز چلائیں:
pkg update && pkg install python git -y
pip install google-genai openai
2. API Keys سیٹ کریں
export GEMINI_API_KEY="your_key"
export DEEPSEEK_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
3. چلائیں
git clone https://github.com/apiload5/repo-fixer/
cd repo-fixer
python main.py
---

💰 Cost Estimate | لاگت

*English:* With DeepSeek V4 Flash, 1 full repo scan costs ∼$0.02  
*اردو:* DeepSeek V4 Flash کے ساتھ 1 مکمل Scan کی لاگت ∼$0.02 ہے

---

⚠️ Disclaimer
This tool overwrites files. A backup commit is always created first. Use at your own risk.

*نوٹ:* یہ ٹول فائلوں کو Overwrite کرتا ہے۔ پہلے ہمیشہ Backup Commit بنایا جاتا ہے۔

License
MIT © 2026 apiload5

**Push karne ke commands**
```bash
cd repo-fixer
git add README.md main.py tokens_state.json repo_config.json
git commit -m "Release: Repo-Fixer v2.1 - Bilingual README Added"
git push origin main
Link: `https://github.com/apiload5/repo-fixer/`

