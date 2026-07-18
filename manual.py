import os
import subprocess
import re
import json
import random
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Optional

# Configuration
EXTENSIONS = [".ts", ".tsx", ".js", ".jsx", ".py", ".php", ".go", ".rs", ".java", ".c", ".cpp"]
BACKUP_DIR = "backups"
LOG_FILE = "fixer_log.json"

DEBUG = True

def debug_print(msg: str, level: str = "INFO"):
    if DEBUG:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {msg}")
        sys.stdout.flush()

class FixerLogger:
    def __init__(self):
        self.logs = []
        self.fixed_count = 0
    
    def log(self, action: str, file: str, status: str, details: str = ""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "file": file,
            "status": status,
            "details": details
        }
        self.logs.append(entry)
        if status == "FIXED":
            self.fixed_count += 1
        try:
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, indent=2)
        except Exception:
            pass

logger = FixerLogger()

def read_file_safe(file_path: str) -> str:
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc, errors='ignore') as f:
                return f.read()
        except:
            continue
    return ""

def backup_file(file_path: str) -> bool:
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = Path(file_path).name
        backup_path = os.path.join(BACKUP_DIR, f"{file_name}_{timestamp}.bak")
        content = read_file_safe(file_path)
        if content:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    except Exception as e:
        logger.log("BACKUP", file_path, "ERROR", str(e))
    return False

def detect_build_system(repo_path: str) -> tuple[str, List[str]]:
    package_json = os.path.join(repo_path, "package.json")
    if os.path.exists(package_json):
        if os.path.exists(os.path.join(repo_path, "pnpm-lock.yaml")):
            return "pnpm", ["pnpm", "run", "build"]
        if os.path.exists(os.path.join(repo_path, "bun.lockb")):
            return "bun", ["bun", "run", "build"]
        return "npm", ["npm", "run", "build"]
    if os.path.exists(os.path.join(repo_path, "Cargo.toml")):
        return "cargo", ["cargo", "build"]
    if os.path.exists(os.path.join(repo_path, "go.mod")):
        return "go", ["go", "build"]
    return "python", [sys.executable, "-m", "py_compile"]

def run_build(repo_path: str) -> str:
    build_type, cmd = detect_build_system(repo_path)
    print(f"🔧 System Clean-check running via: {build_type}")
    original_dir = os.getcwd()
    os.chdir(repo_path)
    try:
        if build_type == "python":
            result = subprocess.run(cmd + ["*.py"], capture_output=True, text=True, shell=True, timeout=60)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return (result.stdout or "") + "\n" + (result.stderr or "")
    except Exception as e:
        return str(e)
    finally:
        os.chdir(original_dir)

def parse_errors(build_output: str) -> List[Dict]:
    errors = []
    # Using Raw string (r"") to fix the escaping warning
    patterns = [
        r"([a-zA-Z0-9_\-\.\/]+\.(?:ts|tsx|js|jsx|py|go|cpp|c|php|java))[\(:](\d+)[,:](\d+)?[\):]?\s*(.*error.*)",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, build_output, re.IGNORECASE)
        for match in matches:
            errors.append({
                "file": match[0],
                "line": match[1],
                "error": match[-1].strip()
            })
    
    seen = set()
    unique = []
    for e in errors:
        key = f"{e['file']}:{e['line']}"
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique

def copy_to_clipboard(text: str) -> bool:
    for cmd in [["termux-clipboard-set"], ["xclip", "-selection", "clipboard"], ["pbcopy"]]:
        try:
            subprocess.run(cmd, input=text.encode(), check=True, stderr=subprocess.DEVNULL)
            return True
        except:
            continue
    return False

def get_from_clipboard() -> str:
    for cmd in [["termux-clipboard-get"], ["xclip", "-selection", "clipboard", "-o"], ["pbpaste"]]:
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except:
            continue
    return ""

def apply_single_fix(file_path: str, ai_response: str) -> bool:
    code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', ai_response, re.DOTALL)
    fixed_code = code_match.group(1) if code_match else ai_response.strip()
    
    if len(fixed_code) > 10:
        if backup_file(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            return True
    return False

def main():
    print("="*70)
    print("=== SMART BATCH CODE REPAIR ENGINE (NO-KEY EDITION) ===")
    print("="*70)

    repo_path = input("📁 Enter Repository Path: ").strip()
    if not os.path.exists(repo_path):
        print("❌ Path invalid.")
        return

    print("\n🔍 Scanning build state & tracking syntax breakdowns...")
    build_out = run_build(repo_path)
    errors = parse_errors(build_out)

    if not errors:
        print("✅ No immediate compilation errors detected in build logs!")
        return

    print(f"\n📊 Found {len(errors)} files with errors. Switching to Step-by-Step Flow Mode...")
    
    for idx, err in enumerate(errors):
        file_rel_path = err['file']
        full_path = os.path.join(repo_path, file_rel_path) if not os.path.isabs(file_rel_path) else file_rel_path
        
        if not os.path.exists(full_path):
            continue
            
        print(f"\n--- [PROCESSING FILE {idx+1}/{len(errors)}] ---")
        print(f"📁 Target: {file_rel_path} (Line: {err['line']})")
        print(f"❌ Error Context: {err['error']}")

        file_content = read_file_safe(full_path)
        
        # Safe Multi-line string concatenation avoiding raw triple-quote compilation glitches
        prompt = (
            "You are an expert debugger. Fix this SPECIFIC file based on the build error.\n"
            "Return ONLY the full corrected code inside a standard markdown code block.\n\n"
            f"TARGET FILE: {file_rel_path}\n"
            f"BUILD ERROR ON THIS FILE: Line {err['line']} -> {err['error']}\n\n"
            "CURRENT FILE CONTENT:\n"
            "```\n"
            f"{file_content}\n"
            "```\n\n"
            "INSTRUCTIONS:\n"
            "1. Fix the error completely.\n"
            "2. Maintain all other logic and modules imports.\n"
            "3. Return the full code block without conversational boilerplate.\n"
        )

        if copy_to_clipboard(prompt):
            print("✨ Prompt auto-copied to clipboard! Go paste it in Gemini/DeepSeek web interface.")
        else:
            print("⚠️ Clipboard access failed. Copy the prompt manually from console output.")
            print("\n--- PROMPT START ---")
            print(prompt)
            print("--- PROMPT END ---\n")

        print("\n⏳ Waiting for you to copy the fixed code from the AI web window...")
        input("👉 Press ENTER once you have COPIED the AI's fixed output code to your clipboard...")

        ai_fix = get_from_clipboard()
        if not ai_fix or "CURRENT FILE CONTENT" in ai_fix:
            print("❌ Clipboard looks empty or contains the old prompt. Let's do a manual input.")
            print("Paste the code below (Press Ctrl+D or Ctrl+Z followed by Enter when done):")
            ai_fix = sys.stdin.read()

        if ai_fix.strip():
            if apply_single_fix(full_path, ai_fix):
                print(f"✅ Success! Fixed and backed up: {file_rel_path}")
                logger.log("PATCH", file_rel_path, "FIXED")
            else:
                print(f"❌ Could not safely extract code block for {file_rel_path}")
        else:
            print("Skip: Module response container was found empty.")

        time.sleep(1)

    print("\n" + "="*70)
    print(f"🎉 BATCH PROCESS RUN COMPLETE! Files updated: {logger.fixed_count}")
    print(f"💾 Rollbacks saved in: ./{BACKUP_DIR}/")
    print("="*70)

if __name__ == "__main__":
    main()
