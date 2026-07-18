import os, subprocess, json, requests, time, glob, re

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
MAX_CHARS = 80000 # ~20k tokens ka 1 chunk

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def call_gemini_api(prompt, api_key):
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.05, "maxOutputTokens": 8192}}
    url = f"{GEMINI_URL}?key={api_key}"
    for attempt in range(2):
        try:
            res = requests.post(url, headers=headers, json=data, timeout=300)
            res_json = res.json()
            if "error" in res_json: print(f"❌ API Error: {res_json['error']['message']}"); return ""
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        except: time.sleep(10)
    return ""

def get_repo_files(repo_path):
    files = []
    extensions = ('*.py', '*.js', '*.ts', '*.jsx', '*.tsx')
    for ext in extensions: files.extend(glob.glob(os.path.join(repo_path, '**', ext), recursive=True))
    return [f for f in files if '.git' not in f]

def apply_fixes(repo_path, result_text):
    pattern = r'--- FILE: (.*?) ---\n(.*?)(?=\n--- FILE: |\Z)'
    matches = re.findall(pattern, result_text, re.DOTALL)
    fixed = 0
    for filepath, code in matches:
        filepath = filepath.strip()
        code = code.strip()
        try:
            with open(filepath, 'w', encoding='utf-8') as f: f.write(code)
            print(f" ✅ Fixed: {os.path.relpath(filepath, repo_path)}")
            fixed += 1
        except: print(f" ❌ Failed to write: {filepath}")
    return fixed

def main():
    print("=============================================")
    print("💎 AI REPOSITORY SELF-HEALING ENGINE - TOKEN MODE v5.1")
    print("=============================================\n")

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key: print("❌ GEMINI_API_KEY set nahi hai."); return

    repo_path = input("📁 Enter repo path: ").strip()
    if not os.path.exists(repo_path): print("❌ Path nahi mila."); return

    print("\n📥 Git Pull...")
    run(f"cd '{repo_path}' && git pull")
    run(f"cd '{repo_path}' && git add -A && git commit -m 'AI Backup before auto-fix' --allow-empty")

    files = get_repo_files(repo_path)
    print(f"\n🔍 {len(files)} files mili hain. Chunks bana raha hun...")

    chunk, file_count = "", 0
    total_fixed = 0
    for i, file in enumerate(files):
        try:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f: code = f.read()
            if len(code) < 10: continue
            new_chunk = chunk + f"\n\n--- FILE: {file} ---\n{code}"
            if len(new_chunk) > MAX_CHARS or i == len(files)-1:
                print(f"\n🧠 Sending chunk {file_count+1} to Gemini...")
                prompt = f"You are an expert code fixer. Fix all bugs, syntax errors, and logic issues in the code below.\nReturn the COMPLETE fixed code for EACH file with this exact separator: --- FILE: full_path ---\nNo explanation, no markdown.\n{chunk}"
                result = call_gemini_api(prompt, gemini_key)
                if result: total_fixed += apply_fixes(repo_path, result)
                chunk, file_count = new_chunk, file_count + 1
                time.sleep(12) # quota bachane ke liye
            else:
                chunk = new_chunk
        except: continue

    print(f"\n✅ Kaam khatam! Total {total_fixed} files fix ho gayin!")

    push = input("\n🚀 Kya changes ko origin/main par push karna hai? (y/n): ").lower()
    if push == 'y':
        run(f"cd '{repo_path}' && git add -A && git commit -m 'AI Auto-Fix by Gemini 2.0 Token Mode' && git push")
        print("✅ Push ho gaya!")

    print("\n🎉 Done!")

if __name__ == "__main__": main()
