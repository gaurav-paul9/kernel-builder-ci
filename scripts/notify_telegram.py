#!/usr/bin/env python3
import sys
import os
import json
import glob
import urllib.request
def parse_env_file(filepath):
    data = {}
    if not os.path.isfile(filepath):
        return data
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data

def main():
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    if not bot_token or not chat_id:
        print("[Telegram] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured in secrets. Skipping notification.")
        sys.exit(0)

    if len(sys.argv) < 5:
        print("Usage: notify_telegram.py <rom> <sublevel> <tag_name> <date_display> [repo] [assets_dir]")
        sys.exit(0)

    rom = sys.argv[1]
    sublevel = sys.argv[2]
    tag_name = sys.argv[3]
    date_display = sys.argv[4]
    gh_repo = sys.argv[5] if len(sys.argv) > 5 else "gaurav-paul9/kernel-builder-ci"
    assets_dir = sys.argv[6] if len(sys.argv) > 6 else "release_assets"

    release_url = f"https://github.com/{gh_repo}/releases/tag/{tag_name}"

    # Scan metadata files
    meta_files = glob.glob(os.path.join(assets_dir, "metadata_*.env"))
    variants_info = {}
    kernel_short_sha = ""
    modules_short_sha = ""
    kernel_repo = ""
    modules_repo = ""

    for mf in sorted(meta_files):
        env_data = parse_env_file(mf)
        v = env_data.get("VARIANT")
        if v:
            variants_info[v] = env_data
        if not kernel_short_sha and env_data.get("KERNEL_SHORT_SHA"):
            kernel_short_sha = env_data["KERNEL_SHORT_SHA"]
        if not modules_short_sha and env_data.get("MODULES_SHORT_SHA"):
            modules_short_sha = env_data["MODULES_SHORT_SHA"]
        if not kernel_repo and env_data.get("KERNEL_REPO"):
            kernel_repo = env_data["KERNEL_REPO"]
        if not modules_repo and env_data.get("MODULES_REPO"):
            modules_repo = env_data["MODULES_REPO"]

    if rom.lower() == "yaap":
        kernel_repo = kernel_repo or "https://github.com/gaurav-paul9/android_kernel_oneplus_sm8550"
        modules_repo = modules_repo or "https://github.com/gaurav-paul9/android_kernel_oneplus_sm8550-modules"
    else:
        kernel_repo = kernel_repo or "https://github.com/OnePlus12R-development/android_kernel_oneplus_sm8550"
        modules_repo = modules_repo or "https://github.com/gaurav-paul9/android_kernel_oneplus_sm8550-modules"

    k_link = f"<a href='{kernel_repo}'>kernel</a>" + (f" (<code>{kernel_short_sha}</code>)" if kernel_short_sha else "")
    m_link = f"<a href='{modules_repo}'>modules</a>" + (f" (<code>{modules_short_sha}</code>)" if modules_short_sha else "")

    # Build image bullet points
    images_text = []
    boot_items = [
        ("vanilla", "boot.img", "Vanilla / Clean Stock ROM"),
        ("ksun", "boot-ksun.img", "KernelSU-Next (dev)"),
        ("ksun-susfs", "boot-ksun-susfs.img", "KernelSU-Next (dev-susfs) + SuSFS"),
        ("resukisu-susfs", "boot-resuki-susfs.img", "BakaSU (ReSukiSU) + SuSFS")
    ]

    for var, img, def_desc in boot_items:
        if var in variants_info:
            desc = variants_info[var].get("ROOT_DESC") or def_desc
            images_text.append(f"• <code>{img}</code>: {desc}")
        elif not variants_info:
            images_text.append(f"• <code>{img}</code>: {def_desc}")

    boot_summary = "\n".join(images_text)

    msg = f"""🔥 <b>New Kernel Release for OnePlus 12R (Aston)</b>

📱 <b>ROM:</b> #{rom}
🐧 <b>Kernel:</b> Linux 5.15.{sublevel} (SM8550)
⏰ <b>Build Time:</b> {date_display}

🔗 <b>Source Trees:</b>
• Kernel Tree: {k_link}
• Modules Tree: {m_link}

📦 <b>Available Boot Images:</b>
{boot_summary}

⚡ <b>Flash Command:</b>
<code>fastboot flash boot &lt;boot_image_name&gt;.img</code>

📥 <b>Download & Checksums:</b>
👉 <a href="{release_url}">GitHub Release Page</a>
"""

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            if resp_data.get("ok"):
                print("[Telegram] Successfully published release post to Telegram channel!")
            else:
                print(f"[Telegram] Failed to post to Telegram: {resp_data}")
    except Exception as e:
        print(f"[Telegram] Error sending Telegram message: {e}")

if __name__ == "__main__":
    main()
