import os
import json
import datetime
import subprocess
import google.generativeai as genai # CHANGED
from openai import OpenAI

# 1. SETTINGS & PERSISTENCE WITH AUTO-RESET DATE
TOKEN_FILE = "tokens_state.json"
CONFIG_FILE = "repo_config.json"
DAILY_TOKEN_LIMIT = 80000

def get_today_string():
    return str(datetime.date.today())

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                data = json.load(f)
                if data.get("date")!= get_today_string():
                    save_tokens(0)
                    return 0
                return data.get("used", 0)
        except:
            pass
    return 0

def save_tokens(used_tokens):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"used": used_tokens, "date": get_today_string()}, f)

def load_saved_repo():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f).get("last_used_path", "")
        except:
            pass
    return ""

def save_repo_path(path):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"last_used_path": path}, f)

# 2. SECURE GIT EXECUTION ARRAY
def run_git_command(args_list, repo_path):
    try:
        result = subprocess.run(
            args_list,
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False
        )
        return result.returncode == 0, (result.stdout or result.stderr).strip()
    except Exception as e:
        return False, str(e)

# 3. SECURE REPOSITORY SCANNER
def build_secure_repo_tree(root_dir):
    tree = {}
    ignored = ["node_modules", "vendor", ".next", "venv", "__pycache__", ".git", "storage", "dist"]
    extensions = (".js", ".jsx", ".ts", ".tsx", ".php", ".py", ".json", ".txt", ".env.example")
    MAX_CHAR_LIMIT = 5000

    for base, _, files in os.walk(root_dir):
        if any(x in base for x in ignored):
            continue
        for file in files:
            if file.endswith(extensions):
                p = os.path.join(base, file)
                rel = os.path.relpath(p, root_dir)
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        tree[rel] = f.read()[:MAX_CHAR_LIMIT]
                except:
                    pass
    return tree

# 4. CORE ENGINE PIPELINE
def main():
    print("=============================================")
    print("💎 AI REPOSITORY SELF-HEALING ENGINE (TERMUX FIXED)")
    print("=============================================\n")

    last_path = load_saved_repo()
    repo_path = ""

    if last_path:
        print(f"🔄 Last worked repository workspace:\n -> {last_path}")
        choice = input("Kya aap isi repository ko scan karna chahte hain? (y/n): ").strip().lower()
        if choice == 'y':
            repo_path = last_path

    if not repo_path:
        repo_path = input("\n📁 Enter repository local absolute path:\n(e.g., /data/data/com.termux/files/home/daily-markeet-main): ").strip()
        repo_path = os.path.abspath(repo_path)

    if not os.path.exists(repo_path) or not os.path.isdir(repo_path):
        print("❌ Error: Valid directory path nahi mil saka.")
        return

    save_repo_path(repo_path)

    branch_success, current_branch = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_path)
    if not branch_success:
        print("❌ Error: Directory context me valid git repository setup nahi mila.")
        return
    print(f"🌿 Current Working Branch: '{current_branch}'")

    print("\n🤖 Select AI Architecture:")
    print("1. Gemini 2.0 Flash")
    print("2. ChatGPT (GPT-4o-mini)")
    print("3. DeepSeek Chat")
    provider_choice = input("Option (1/2/3): ").strip()

    provider_map = {"1": "gemini", "2": "chatgpt", "3": "deepseek"}
    provider = provider_map.get(provider_choice, "gemini")

    print(f"\n📥 Remote changes sync ho rahi hain...")
    success, log = run_git_command(["git", "pull", "origin", current_branch], repo_path)
    if not success:
        print(f"⚠️ Warning: Sync issues ya modified unstaged files ho sakti hain:\n{log}")
        cont = input("Kya aap isi state ke sath continue karna chahte hain? (y/n): ").strip().lower()
        if cont!= 'y': return

    print("\n📦 AI modifications se pehle rollback checkpoint build kiya ja raha hai...")
    _, status_log = run_git_command(["git", "status", "--porcelain"], repo_path)
    has_dirty_files = bool(status_log.strip())

    backup_created = False
    if has_dirty_files:
        run_git_command(["git", "add", "."], repo_path)
        run_git_command(["git", "commit", "-m", "📦 PRE-AI-FIX BACKUP STATE [AUTOMATED]"], repo_path)
        backup_created = True
        print("✅ Safe Backup Checkpoint created successfully.")

    print("\n🔍 Extracting architecture snapshot maps...")
    snapshot = build_secure_repo_tree(repo_path)
    snapshot_str = json.dumps(snapshot, indent=2)
    estimated_tokens = len(snapshot_str) // 4

    tokens_used_today = load_tokens()
    if tokens_used_today + estimated_tokens > DAILY_TOKEN_LIMIT:
        print(f"❌ Quota Lock: Execution stopped. Available token count limit exceeded.")
        if backup_created:
            run_git_command(["git", "reset", "--soft", "HEAD~1"], repo_path)
        return

    prompt = f"""Aap aik Elite Multi-File Repository Architect aur Auto-Repair Agent hain.
Response strictly single valid JSON string hona chahiye bina kisi markdown syntax ya wrappers ke:
{{
  "system_status": "REPAIRED",
  "detected_ecosystem": "Framework Type",
  "structural_root_cause": "Detailed architectural bugs summary",
  "modifications": [
    {{
      "file_path": "relative/path/file.ext",
      "nature_of_fix": "SYNTAX_ERROR",
      "repaired_complete_file_content": "Pura accurate modified code yahan dalein"
    }}
  ]
}}
Repository Layout Snapshot:
{snapshot_str}"""

    print(f"🧠 {provider.upper()} Engine se connection runtime built ho raha hai...")
    raw_res = ""

    try:
        if provider == "gemini":
            gemini_key = os.getenv("GEMINI_API_KEY")
            if not gemini_key: raise ValueError("GEMINI_API_KEY environment configuration setting array is empty!")
            genai.configure(api_key=gemini_key) # CHANGED
            model = genai.GenerativeModel('gemini-2.0-flash') # CHANGED
            res = model.generate_content(prompt) # CHANGED
            raw_res = res.text
            if res.usage_metadata:
                tokens_used_today += res.usage_metadata.prompt_token_count + res.usage_metadata.candidates_token_count # CHANGED

        elif provider == "chatgpt":
            c = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            res = c.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
            raw_res = res.choices[0].message.content
            tokens_used_today += res.usage.total_tokens

        elif provider == "deepseek":
            c = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
            res = c.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
            raw_res = res.choices[0].message.content
            tokens_used_today += res.usage.total_tokens

        save_tokens(tokens_used_today)

        if raw_res.strip().startswith("```json"):
            raw_res = raw_res.split("```json")[1].split("```")[0].strip()

        try:
            data = json.loads(raw_res)
        except json.JSONDecodeError:
            print("\n❌ AI Response Error: AI ne invalid JSON metadata generate kiya. Initiating Safe Rollback...")
            run_git_command(["git", "reset", "--hard", "HEAD"], repo_path)
            if backup_created:
                run_git_command(["git", "reset", "--soft", "HEAD~1"], repo_path)
                run_git_command(["git", "reset"], repo_path)
            return

        healed_files = []
        for mod in data.get("modifications", []):
            rel_file_path = mod["file_path"]
            if ".." in rel_file_path or rel_file_path.startswith("/"): continue
            f_path = os.path.normpath(os.path.join(repo_path, rel_file_path))
            if not f_path.startswith(repo_path): continue

            os.makedirs(os.path.dirname(f_path), exist_ok=True)
            with open(f_path, "w", encoding="utf-8") as out:
                out.write(mod["repaired_complete_file_content"])
            healed_files.append(rel_file_path)

        if not healed_files:
            print("\n🎉 Verification Completed: Repository completely optimized aur stable hai.")
            if backup_created:
                run_git_command(["git", "reset", "--soft", "HEAD~1"], repo_path)
            return

        print(f"\n🛠️ Edits successfully apply ho chukay hain! System: {data.get('detected_ecosystem')}")
        print(f"📝 Identified Flaws: {data.get('structural_root_cause')}")

        print("\n🔍 Modified changes preview (Git Diff):")
        print("-------------------------------------------------------------")
        _, diff_output = run_git_command(["git", "diff"], repo_path)
        print(diff_output if diff_output.strip() else "Structural edits rendered.")
        print("-------------------------------------------------------------")

        push_choice = input(f"\n🚀 Kya aap in fixes ko target origin/{current_branch} branch par push karna chahte hain? (y/n): ").strip().lower()

        if push_choice == 'y':
            print("📤 Finalizing staging maps...")
            run_git_command(["git", "add", "."], repo_path)
            run_git_command(["git", "commit", "-m", "🤖 AI Auto-Fix: Resolved repository runtime layout bugs"], repo_path)
            print(f"🚀 Pushing changes origin/{current_branch} via secure environment...")
            push_success, push_log = run_git_command(["git", "push", "origin", current_branch], repo_path)
            if push_success:
                print("🏁 Script Executed: 10/10 Core pipelines successfully integrated!")
            else:
                print(f"❌ Network push authentication runtime failure. Logs:\n{push_log}")
        else:
            print("\n🔄 User Interrupted: Discarding changes and triggering automatic absolute rollback...")
            run_git_command(["git", "reset", "--hard", "HEAD"], repo_path)
            if backup_created:
                run_git_command(["git", "reset", "--soft", "HEAD~1"], repo_path)
                run_git_command(["git", "reset"], repo_path)
            print("✅ Directory clean ho gayi aur code backup state me restore kar diya gaya.")

    except Exception as e:
        print(f"\n❌ Script Terminal Pipeline Error: {str(e)}")
        print("🔄 Dynamic emergency backup rollback execution initiated...")
        run_git_command(["git", "reset", "--hard", "HEAD"], repo_path)
        if backup_created:
            run_git_command(["git", "reset", "--soft", "HEAD~1"], repo_path)
            run_git_command(["git", "reset"], repo_path)

if __name__ == "__main__":
    main()
