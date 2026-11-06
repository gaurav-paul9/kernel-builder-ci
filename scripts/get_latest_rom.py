#!/usr/bin/env python3
import sys
import os
import urllib.request
import re

def get_latest_rom(rom):
    url = f"https://files.gauravbuilds.xyz/release/aston/{rom}/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8")
        # Match zip hrefs: href="Lunaris-*.zip" or href="./Lunaris-*.zip"
        matches = re.findall(r'href=[\x22\x27](?:\./)?([^\x22\x27/]+\.zip)[\x22\x27]', html)
        if matches:
            # Sort lexicographically / by date suffix
            unique_zips = sorted(list(set(matches)))
            return unique_zips[-1]
    except Exception as e:
        print(f"[get_latest_rom] Warning: Failed to query {url}: {e}", file=sys.stderr)

    # Fallbacks if server is unreachable
    if rom.lower() == "lunaris":
        return "Lunaris-AOSP-aston-Community-3.13-GMS-2026110109.zip"
    elif rom.lower() == "yaap":
        return "YAAP-17-HOMEMADE-aston-20261003.zip"
    return "Unknown"

def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else "Lunaris"
    latest_zip = get_latest_rom(rom)
    print(f"Latest {rom} ZIP: {latest_zip}")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output and os.path.exists(github_output):
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"latest_rom_zip={latest_zip}\n")

if __name__ == "__main__":
    main()

