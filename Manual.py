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

# Requests module ko explicitly import kiya kyunki call_deepseek_api me use ho raha hai
try:
    import requests
except ImportError:
    pass

# ============ CONFIGURATION ============
DEEPSEEK_API_KEY = "sk-Your-DeepSeek-API-Key-Here"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

EXTENSIONS = [".ts", ".tsx", ".js", ".jsx", ".py", ".php", ".go", ".rs", ".java", ".c", ".cpp"]
BACKUP_DIR = "backups"
LOG_FILE = "fixer_log.json"
MAX_CODE_LENGTH = 20000
RANDOM_FILES_COUNT = 5  

# ============ DEBUG MODE ============
DEBUG = True

def debug_print(msg: str, level: str = "INFO"):
    if DEBUG:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {msg}")
        sys.stdout.flush()

# ============ LOGGING SYSTEM ============
class FixerLogger:
    def __init__(self):
        self.logs = []
        self.fixed_count = 0
        self.error_count = 0
    
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
        elif status in ["ERROR", "FAILED"]:
            self.error_count += 1
            
        with open(LOG_FILE, 'w') as f:
            json.dump(self.logs, f, indent=2)
        
        emoji = "✅" if status == "FIXED" else "⚠️" if status == "WARNING" else "❌"
        print(f"{emoji} [{status}] {action}: {file}")

logger = FixerLogger()

# ============ FILE OPERATIONS ============
def backup_file(file_path: str) -> bool:
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = Path(file_path).name
        backup_path = f"{BACKUP_DIR}/{file_name}_{timestamp}.bak"
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        logger.log("BACKUP", file_path, "ERROR", str(e))
        return False

def read_file_safe(file_path: str) -> str:
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read()
        except:
            continue
    return ""

# ============ DETECT BUILD SYSTEM ============
def detect_build_system(repo_path: str) -> tuple[str, List[str]]:
    debug_print(f"Detecting build system in: {repo_path}")
    
    package_json_path = os.path.join(repo_path, "package.json")
    if os.path.exists(package_json_path):
        debug_print("Found package.json")
        try:
            with open(package_json_path, 'r') as f:
                data = json.load(f)
                scripts = data.get("scripts", {})
                if "build" in scripts:
                    return "npm", ["npm", "run", "build"]
                elif "bundle" in scripts:
                    return "bun", ["bun", "run", "bundle"]
        except Exception as e:
            debug_print(f"Error reading package.json: {e}", "WARNING")
            
    if os.path.exists(os.path.join(repo_path, "Cargo.toml")):
        return "cargo", ["cargo", "build"]
    elif os.path.exists(os.path.join(repo_path, "go.mod")):
        return "go", ["go", "build"]
    
    return "unknown", ["echo", "No build command"]

def run_build(repo_path: str) -> tuple[str, bool]:
    debug_print("Running build...")
    build_type, cmd = detect_build_system(repo_path)
    print(f"\n🔧 Build system: {build_type}")
    
    # Save current directory to revert later
    original_dir = os.getcwd()
    os.chdir(repo_path)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        success = result.returncode == 0
        logger.log("BUILD", repo_path, "SUCCESS" if success else "FAILED", f"Exit: {result.returncode}")
        return output, success
    except subprocess.TimeoutExpired:
        logger.log("BUILD", repo_path, "TIMEOUT", ">5 minutes")
        return "Build timeout", False
    except Exception as e:
        logger.log("BUILD", repo_path, "ERROR", str(e))
        return str(e), False
    finally:
        os.chdir(original_dir)

# ============ ERROR PARSING ============
def parse_errors(build_output: str) -> List[Dict]:
    debug_print("Parsing build errors...")
    errors = []
    
    patterns = [
        r"(.+\.(ts|tsx|js|jsx))[\(:](\d+)[,:](\d+)[\):]?\s*(error.*)",
        r"(.+\.py):(\d+):(\d+)?\s*(error.*)",
        r"(.+\.php):(\d+)\s*(error.*)",
        r"(.+\.(c|cpp)):(\d+):(\d+)?\s*(error.*)",
        r"(.+\.go):(\d+):(\d+)?\s*(error.*)",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, build_output, re.IGNORECASE)
        for match in matches:
            errors.append({
                "file": match[0],
                "line": match[1] if len(match) > 1 else "1",
                "column": match[2] if len(match) > 2 else "1",
                "error": match[-1] if len(match) > 1 else "Unknown error"
            })
    
    seen = set()
    unique_errors = []
    for error in errors:
        key = f"{error['file']}:{error['line']}"
        if key not in seen:
            seen.add(key)
            unique_errors.append(error)
    
    logger.log("PARSE", "Build output", "SUCCESS", f"Found {len(unique_errors)} errors")
    return unique_errors

# ============ COLLECT FILES ============
def collect_files(repo_path: str, errors: List[Dict]) -> List[str]:
    debug_print("Collecting files to check...")
    files_to_check = set()
    
    for error in errors:
        files_to_check.add(error['file'])
        debug_print(f"Added error file: {error['file']}")
    
    all_files = []
    for ext in EXTENSIONS:
        debug_print(f"Searching for *{ext} files...")
        found = list(Path(repo_path).rglob(f"*{ext}"))
        found = [str(f) for f in found if not any(x in str(f).split(os.sep) for x in ['node_modules', '.git', '__pycache__', 'target', 'dist', 'build'])]
        all_files.extend(found)
        debug_print(f"Found {len(found)} {ext} files")
    
    debug_print(f"Total files found: {len(all_files)}")
    
    random_count = min(RANDOM_FILES_COUNT, len(all_files))
    if random_count > 0:
        random_files = random.sample(all_files, random_count)
        files_to_check.update(random_files)
        debug_print(f"Added {random_count} random files")
    
    result = list(files_to_check)
    debug_print(f"Total files to check: {len(result)}")
    return result

# ============ PREPARE PROMPT ============
def prepare_ai_prompt(repo_path: str, errors: List[Dict], files_to_check: List[str]) -> str:
    debug_print("Preparing AI prompt...")
    code_dump = ""
    count = 0
    
    for file in files_to_check[:10]:
        if os.path.exists(file):
            content = read_file_safe(file)
            if content and len(content) > 10:
                code_dump += f"\n\n--- FILE: {file} ---\n{content[:1000]}\n...\n--- END ---\n"
                count += 1
                debug_print(f"Added file {count}: {Path(file).name}")
    
    debug_print(f"Added {count} files to prompt")
    
    prompt = f"""You are a senior developer. Fix ALL issues in this codebase.

BUILD ERRORS TO FIX:
{json.dumps(errors[:10], indent=2)}

CODEBASE CONTEXT:
{code_dump[:MAX_CODE_LENGTH]}

FIX REQUIREMENTS:
1. Fix ALL build errors first
2. Fix logic bugs and state issues
3. Add proper error handling
4. Fix security issues

RESPONSE FORMAT:
For EACH file that needs fixing, output:

FILE: /full/path/to/file.ext
FIX:
```language
// Complete fixed file content

```

START FIXING NOW:"""

```
debug_print(f"Prompt length: {len(prompt)} characters")
return prompt

```

# ============ DEEPSEEK API ============

def call_deepseek_api(prompt: str) -> Optional[str]:
debug_print("Calling DeepSeek API...")

```
if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "sk-Your-DeepSeek-API-Key-Here":
    print("\n⚠️ DeepSeek API key not configured!")
    return None

headers = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "deepseek-coder",
    "messages": [
        {"role": "system", "content": "You are an expert code fixer. Return complete fixed files."},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.3,
    "max_tokens": 6000
}

try:
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=120)
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        print(f"❌ API Error: {response.status_code}")
        return None
except Exception as e:
    print(f"❌ API Exception: {e}")
    return None

```

# ============ APPLY FIXES ============

def apply_fixes(ai_response: str) -> int:
debug_print("Applying fixes...")
fixed_count = 0

```
if not ai_response:
    return 0

sections = re.split(r'FILE:\s*', ai_response)
debug_print(f"Found {len(sections)-1} file sections")

for section in sections[1:]:
    try:
        lines = section.strip().split('\n')
        if not lines:
            continue
        
        file_path = lines[0].strip()
        if not file_path or not os.path.exists(file_path):
            debug_print(f"File not found: {file_path}")
            continue
        
        content = '\n'.join(lines[1:])
        code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', content, re.DOTALL)
        
        if code_match:
            fixed_code = code_match.group(1)
        else:
            if "FIX:" in content:
                fixed_code = content.split("FIX:", 1)[1].strip()
            else:
                fixed_code = content.strip()
        
        if not fixed_code or len(fixed_code) < 10:
            debug_print(f"Skipping {file_path} - code too short")
            continue
        
        if backup_file(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            fixed_count += 1
            logger.log("APPLY_FIX", file_path, "FIXED", "Success")
            print(f"✅ FIXED: {file_path}")
    
    except Exception as e:
        logger.log("APPLY_FIX", "Unknown", "ERROR", str(e))
        continue

return fixed_count

```

# ============ MAIN ============

def main():
print("="*70)
print("=== REPO FIXER v13.1 - FIXED MODE ===")
print("="*70)

```
repo_path = input("\n📁 Enter repository path: ").strip()
if not os.path.exists(repo_path):
    print("❌ Path does not exist!")
    return

print(f"\n📂 Working on: {repo_path}")
print(f"🐛 Debug mode: ON")

print("\n[1/4] Running build...")
build_output, build_success = run_build(repo_path)
errors = parse_errors(build_output)

print(f"\n📊 Found {len(errors)} build errors")

if errors:
    for i, error in enumerate(errors[:5]):
        print(f"   {i+1}. {error['file']}:{error['line']} - {error['error'][:50]}")

print("\n[2/4] Collecting files...")
files_to_check = collect_files(repo_path, errors)
print(f"📁 {len(files_to_check)} files will be checked")

print("\n[3/4] Preparing AI prompt...")
prompt = prepare_ai_prompt(repo_path, errors, files_to_check)

print("\n📝 Prompt preview (first 500 chars):")
print("="*50)
print(prompt[:500] + "...")
print("="*50)

print("\n[4/4] Getting fixes...")

ai_response = None
if DEEPSEEK_API_KEY and DEEPSEEK_API_KEY != "sk-Your-DeepSeek-API-Key-Here":
    try:
        ai_response = call_deepseek_api(prompt)
    except Exception as e:
        print(f"⚠️ API calling main framework issue: {e}")

if not ai_response:
    print("\n📋 Switching to manual mode...")
    try:
        subprocess.run(["termux-clipboard-set"], input=prompt.encode(), check=True)
        print("✅ Prompt copied to clipboard")
    except:
        pass
    
    input("\nPress ENTER after pasting in Gemini/AI and copying response...")
    
    try:
        ai_response = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True).stdout
    except:
        ai_response = input("Paste AI response: ")

if ai_response:
    print("\n[5/5] Applying fixes...")
    fixed_count = apply_fixes(ai_response)
    
    print("\n" + "="*70)
    print("✅ FIX COMPLETE!")
    print("="*70)
    print(f"📝 Files fixed: {fixed_count}")
    print(f"💾 Backups: {BACKUP_DIR}/")
    print(f"📋 Logs: {LOG_FILE}")
else:
    print("\n❌ No AI response received!")

```

if **name** == "**main**":
try:
main()
except KeyboardInterrupt:
print("\n\n⚠️ Interrupted by user")
except Exception as e:
print(f"\n❌ Error: {e}")
import traceback
traceback.print_exc()
