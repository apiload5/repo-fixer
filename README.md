### 🤖 Repo-Fixer: Automated Self-Healing CLI Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Termux Compatible](https://img.shields.io/badge/Termux-Compatible-green.svg)](https://termux.com/)

> **English:** Repo-Fixer is an intelligent, interactive Terminal-based (CLI) utility that dynamically audits your full-stack source codebases (Next.js, Laravel, Django, Python, etc.), traces bugs and syntax errors, and automatically repairs them on local disk using AI engines (Gemini, ChatGPT, DeepSeek).

> **اردو:** Repo-Fixer ایک ذہین، انٹرایکٹو Terminal پر مبنی (CLI) یوٹیلیٹی ہے جو آپ کے Full-Stack سورس کوڈبیسز (Next.js, Laravel, Django, Python وغیرہ) کو ڈائنامکلی آڈٹ کرتی ہے، Bugs اور Syntax Errors کو ٹریس کرتی ہے، اور AI انجنز (Gemini, ChatGPT, DeepSeek) کا استعمال کرکے انہیں لوکل ڈسک پر خودکار طریقے سے Repair کر دیتی ہے۔

This tool is specifically optimized for **Termux** (Android mobile shell) and lightweight setups without any heavy local machine framework dependencies.

---

## 🔥 Features & Production Safeguards

### English 🇬🇧
- 📦 **Fully Interactive CLI**: On launch it asks for the last repository workspace path. Continue with a single-key click.
- 📥 **Native Git & SSH Automation**: Automatically `git pull` latest changes and `git push` to target remote branch after repair.
- 🛡️ **Command Injection Shield**: Built with pure list-arrays processing (`shell=False`) for zero shell manipulation risks in Termux.
- 🔄 **Safe Rollback Checkpoint**: Creates a local snapshot commit before AI injection. If AI fails or you reject the preview, code restores in seconds.
- 🔍 **Live Git Diff Preview**: Shows a complete preview of code modifications before pushing to GitHub.
- ⏳ **Token Quota Persistence**: Daily usage saved in `tokens_state.json` and auto-resets on a new day.

### اردو 🇵🇰
- 📦 **مکمل انٹرایکٹو CLI**: چلتے ہی پچھلی Repository کا Path پوچھتا ہے۔ ایک Key دبانے سے کام جاری۔
- 📥 **نیٹو Git اور SSH آٹومیشن**: Repair کے بعد خودکار `git pull` اور `git push` کرتا ہے۔
- 🛡️ **کمانڈ انجیکشن شیلڈ**: `shell=False` لسٹ ایریز پر بنی ہے۔ Termux میں 100% سیکیور ہے۔
- 🔄 **سیف رول بیک چیک پوائنٹ**: AI سے پہلے Backup Commit بناتا ہے۔ اگر AI فیل ہو یا آپ `n` دبائیں تو کوڈ واپس ریسٹور۔
- 🔍 **لائیو Git Diff پریویو**: GitHub پر Push سے پہلے تمام تبدیلیاں دکھاتا ہے۔
- ⏳ **ٹوکن کوٹہ پرسیسٹنس**: روزانہ کا استعمال `tokens_state.json` میں محفوظ اور نیا دن شروع ہوتے ہی Auto-Reset۔
```
pip install google-generativeai openai requests
export GEMINI_API_KEY="your_google_key"
python repo-fixer.py
```

**2. Set API Keys:**
```
export GEMINI_API_KEY="your_key"
export DEEPSEEK_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
```

**3. Run:**
```
git clone https://github.com/apiload5/repo-fixer/
cd repo-fixer
python main.py
```

### اردو 🇵🇰

**1. ریکوائرمنٹس سیٹ اپ** - Termux یا Linux Terminal میں یہ کمانڈز چلائیں:
```
export GEMINI_API_KEY="your_key"
export DEEPSEEK_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
```

**3. چلائیں:**
```
git clone https://github.com/apiload5/repo-fixer/
cd repo-fixer
python main.py
```

---

## 💰 Cost Estimate

| English | اردو |
|---------|------|
| With DeepSeek V4 Flash, 1 full repo scan costs ∼$0.02 | DeepSeek V4 Flash کے ساتھ 1 مکمل Scan کی لاگت ∼$0.02 ہے |

---

## ⚠️ Disclaimer

> **English:** This tool overwrites files. A backup commit is always created first. Use at your own risk.
>
> **اردو:** یہ ٹول فائلوں کو Overwrite کرتا ہے۔ پہلے ہمیشہ Backup Commit بنایا جاتا ہے۔

---


## 📝 License

MIT © 2026 [apiload5](https://github.com/apiload5)
This architecture utility is open-source and free for development tracking optimization workloads. Keep your code running smooth, automatically!

---

## 🔗 Links

- **Repository**: https://github.com/apiload5/repo-fixer/
- **Issues**: https://github.com/apiload5/repo-fixer/issues
- **Pull Requests**: https://github.com/apiload5/repo-fixer/pulls

---
# 1. Direct terminal se requirements file create karein
```
cat << 'EOF' > requirements.txt
google-genai>=0.1.1
openai>=1.0.0
pydantic>=2.0.0
EOF

# 2. GitHub par push karein
git add requirements.txt
git commit -m "chore: add production requirements.txt for dependencies"
git push origin main
```
------


