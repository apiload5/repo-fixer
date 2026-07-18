# 💎 Repo-Fixer - AI Repository Self-Healing Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Gemini AI](https://img.shields.io/badge/Gemini-2.0%20Flash-orange.svg)](https://ai.google.dev/gemini)

An AI-powered tool that automatically scans your entire codebase, fixes bugs, syntax errors, and logic issues using **Google Gemini 2.0 Flash**.

Built for **Termux**, **Linux**, and **Mac**. Token-based mode to avoid API quota limits.

---

## ✨ Features

- **Token-Based Scanning**: Joins 10-15 files into 1 API call to save quota
- **Auto Fix + Save**: Scans, fixes, and overwrites files automatically
- **Multi-Language Support**: Python, JS, TS, JSX, TSX, JSON, HTML, CSS
- **Git Integration**: Auto `git pull` and `git commit` backup before fixing
- **Smart Push**: Asks to push fixed code to GitHub automatically
- **Quota Friendly**: 69 files = Only 4-5 API calls instead of 69

---

## 🚀 Quick Start

### 1. Requirements

```bash
# For Termux
pkg update && pkg upgrade
pkg install python git

# For Linux/Mac
sudo apt update && sudo apt install python3 git  # Ubuntu/Debian
brew install python git                          # macOS
```
Install Python dependency:
```
pip install requests
```
2. Get Gemini API Key
Get free key from: Google AI Studio

Free tier: 50 requests/day

Model: gemini-2.0-flash (fastest and most capable)

3. Setup
```
cd ~
git clone https://github.com/YOUR_USERNAME.git
export GEMINI_API_KEY="PASTE_YOUR_KEY_HERE"
```
4. Run
```
python repo-fixer.py
```
When prompted, enter your repo path:
```
/data/data/com.termux/files/home/repository
```
📁 How It Works
graph LR
    A[Scan Repository] --> B[Create Git Backup]
    B --> C[Group Files into Chunks]
    C --> D[Send to Gemini 2.0 Flash]
    D --> E[Parse Fixed Code]
    E --> F[Overwrite Files]
    F --> G[Optional Push to GitHub]
    
