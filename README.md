# 🤖 Repo-Fixer: Automated Self-Healing CLI Engine

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

---


## 🚀 Push Commands

```bash
cd repo-fixer
git add README.md main.py tokens_state.json repo_config.json
git commit -m "Release: Repo-Fixer v2.1 - Bilingual README Added"
git push origin main
```




