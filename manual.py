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

def scan_all_files(repo_path: str) -> List[str]:
    valid_files = []
    ignore_dirs = { 'node_modules', '.git', '__pycache__', 'target', 'dist', 'build', '.next', 'backups' }
    for ext in EXTENSIONS:
        found = list(Path(repo_path).rglob(f"*{ext}"))
        for f in found:
            if not any(x in f.parts for x in ignore_dirs):
                valid_files.append(str(f))
    return valid_files

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

def process_file_pipeline(full_path: str, rel_path: str, issue_desc: str):
    file_content = read_file_safe(full_path)
    prompt = (
        "You are an expert full-stack engineer. Refactor and advance this specific module.\n"
        "Optimize logic, enhance performance, fix hidden runtime edge-cases, and return valid execution blocks.\n\n"
        f"TARGET FILE MODULE: {rel_path}\n"
        f"DEVELOPER CONTEXT/ISSUE: {issue_desc}\n\n"
        "CURRENT CODEBASE OBJECT:\n"
        "```\n"
        f"{file_content}\n"
        "```\n\n"
        "INSTRUCTIONS:\n"
        "1. Re-architect cleanly and fix any underlying code-smell.\n"
        "2. Do not drop structural functional exports or critical features.\n"
        "3. Return ONLY the full updated source code nested in single markdown blocks.\n"
    )

    if copy_to_clipboard(prompt):
        print("\n✨ Prompt auto-copied to system clipboard! Paste it inside your AI chat.")
    else:
        print("\n⚠️ Clipboard access blocked. Copy manually below:")
        print(f"\n--- PROMPT ---\n{prompt}\n--------------\n")

    print("⏳ Processing layout ready on external AI agent...")
    input("👉 Copy updated block from AI, then press [ENTER] here to patch code layout...")

    ai_fix = get_from_clipboard()
    if not ai_fix or "CURRENT CODEBASE OBJECT" in ai_fix:
        print("❌ Clipboard invalid/empty. Switching to manual stream mode.")
        print("Paste fixed block here (Press Ctrl+D when finished):")
        ai_fix = sys.stdin.read()

    if ai_fix.strip():
        if apply_single_fix(full_path, ai_fix):
            print(f"✅ [SUCCESS] Patched module layout: {rel_path}")
            logger.log("ADVANCE", rel_path, "FIXED")
        else:
            print("❌ Error applying structural transformation blocks.")
    else:
        print("⏭️ Pipeline operation bypassed.")

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

    if errors:
        print(f"\n📊 Found {len(errors)} compilation errors! Starting repair chain...")
        for idx, err in enumerate(errors):
            f_path = err['file']
            full_path = os.path.join(repo_path, f_path) if not os.path.isabs(f_path) else f_path
            if os.path.exists(full_path):
                print(f"\n[QUEUE {idx+1}/{len(errors)}] Target: {f_path}")
                process_file_pipeline(full_path, f_path, f"Build error on Line {err['line']}: {err['error']}")
    else:
        print("✅ No compilation errors detected! Entering Custom Refactor/Advance Mode...")
        print("Scanning working files tree structure...")
        all_files = scan_all_files(repo_path)
        
        if not all_files:
            print("❌ No matching source code modules found.")
            return

        print(f"Total source units managed: {len(all_files)}")
        print("\n--- FILE MANIFEST INDEX ---")
        for i, f in enumerate(all_files[:30]): # Show first 30 files
            print(f" [{i+1}] {os.path.relpath(f, repo_path)}")
        if len(all_files) > 30:
            print(f"... and {len(all_files)-30} more files.")

        try:
            choice = input("\n👉 Enter file number to Refactor/Advance (or 'q' to quit): ").strip()
            if choice.lower() == 'q' or not choice:
                return
            
            idx = int(choice) - 1
            if 0 <= idx < len(all_files):
                target_file = all_files[idx]
                rel_target = os.path.relpath(target_file, repo_path)
                issue = input("📝 What should the AI do with this file? (e.g., 'add error handling', 'optimize routing'): ").strip()
                if not issue:
                    issue = "Review, refactor, advance code structure and improve production reliability."
                
                process_file_pipeline(target_file, rel_target, issue)
            else:
                print("❌ Out of range selection.")
        except ValueError:
            print("❌ Action dropped.")

    print("\n" + "="*70)
    print(f"🎉 OPERATION LIFECYCLE COMPLETE! Files updated: {logger.fixed_count}")
    print(f"💾 Backups location: ./{BACKUP_DIR}/")
    print("="*70)

if __name__ == "__main__":
    main()
