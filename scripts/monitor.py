#!/usr/bin/env python3
import urllib.request
import json
import sys
import time
import zipfile
import io
import os

TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
REPO = "gaurav-paul9/kernel-builder-ci"
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Antigravity-CI-Monitor"
}
if TOKEN:
    HEADERS["Authorization"] = f"token {TOKEN}"

def api_get(endpoint):
    url = f"https://api.github.com/repos/{REPO}/{endpoint}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_runs():
    data = api_get("actions/runs?per_page=5")
    return data.get("workflow_runs", [])

def get_run_jobs(run_id):
    data = api_get(f"actions/runs/{run_id}/jobs")
    return data.get("jobs", [])

def trigger_workflow(rom="Yaap", build_type="all", clang_ver="clang-r563880c", branch="", custom_url=""):
    url = f"https://api.github.com/repos/{REPO}/actions/workflows/kernel_ci.yml/dispatches"
    payload = {
        "ref": "main",
        "inputs": {
            "rom": rom,
            "build_type": build_type,
            "clang_version": clang_ver,
            "kernel_branch": branch,
            "custom_boot_url": custom_url
        }
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=HEADERS, method="POST")
    with urllib.request.urlopen(req) as resp:
        print(f"Workflow triggered successfully (Status: {resp.status})")

def show_latest_run_details():
    runs = get_runs()
    if not runs:
        print("No workflow runs found.")
        return
    r = runs[0]
    print(f"=== Latest Workflow Run #{r['run_number']} (ID: {r['id']}) ===")
    print(f"Status:     {r['status']}")
    print(f"Conclusion: {r['conclusion']}")
    print(f"Created At: {r['created_at']}")
    print(f"URL:        {r['html_url']}")
    print("\n--- Jobs Status ---")
    jobs = get_run_jobs(r['id'])
    for j in jobs:
        print(f"[{j['status'].upper()}] {j['name']} -> conclusion: {j['conclusion']}")
        for step in j.get('steps', []):
            if step['conclusion'] == 'failure':
                print(f"   FAILED STEP: {step['name']} (number: {step['number']})")
            elif step['status'] == 'in_progress':
                print(f"   CURRENT STEP: {step['name']}")
    return r, jobs

def get_failed_logs(run_id):
    url = f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}/logs"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            z = zipfile.ZipFile(io.BytesIO(content))
            print("\n=== LOGS SUMMARY ===")
            for name in z.namelist():
                if "fail" in name.lower() or any(x in name for x in ["build", "prepare", "release"]):
                    log_text = z.read(name).decode("utf-8", errors="ignore")
                    lines = log_text.strip().split("\n")
                    # Find errors
                    err_lines = [l for l in lines if any(k in l.lower() for k in ["error:", "failed", "fatal:", "cannot find"])]
                    if err_lines:
                        print(f"\n--- File: {name} (Total lines: {len(lines)}) ---")
                        print("Last 30 lines of log:")
                        print("\n".join(lines[-30:]))
    except Exception as e:
        print(f"Error fetching logs: {e}")

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd == 'status':
        r, jobs = show_latest_run_details()
        if r and r['conclusion'] == 'failure':
            get_failed_logs(r['id'])
    elif cmd == 'trigger':
        rom = sys.argv[2] if len(sys.argv) > 2 else "Yaap"
        btype = sys.argv[3] if len(sys.argv) > 3 else "all"
        trigger_workflow(rom=rom, build_type=btype)
        print("Waiting 5 seconds before checking status...")
        time.sleep(5)
        show_latest_run_details()
    elif cmd == 'logs':
        runs = get_runs()
        if runs:
            get_failed_logs(runs[0]['id'])
