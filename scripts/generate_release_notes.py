#!/usr/bin/env python3
import sys
import os
import glob

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
    if len(sys.argv) < 10:
        print("Usage: generate_release_notes.py <rom> <sublevel> <date_display> <clang_ver> <k_repo> <k_branch> <m_repo> <m_branch> <base_url> [latest_rom_zip] [out_file] [assets_dir]")
        sys.exit(1)

    rom = sys.argv[1]
    sublevel = sys.argv[2]
    date_display = sys.argv[3]
    clang_ver = sys.argv[4]
    k_repo = sys.argv[5].rstrip(".git")
    k_branch = sys.argv[6]
    m_repo = sys.argv[7].rstrip(".git")
    m_branch = sys.argv[8]
    base_url = sys.argv[9]
    latest_rom_zip = sys.argv[10] if len(sys.argv) > 10 and sys.argv[10] and not sys.argv[10].endswith(".md") else "Unknown"
    out_file = sys.argv[11] if len(sys.argv) > 11 else "release_notes.md"
    assets_dir = sys.argv[12] if len(sys.argv) > 12 else "release_assets"

    # Read checksums
    checksums = ""
    chk_file = os.path.join(assets_dir, "SHA256SUMS.txt")
    if not os.path.exists(chk_file) and os.path.exists("SHA256SUMS.txt"):
        chk_file = "SHA256SUMS.txt"
    if os.path.exists(chk_file):
        with open(chk_file, "r", encoding="utf-8", errors="ignore") as f:
            checksums = f.read().strip()

    # Scan metadata files
    meta_files = glob.glob(os.path.join(assets_dir, "metadata_*.env"))
    variants_info = {}
    kernel_sha = ""
    kernel_short_sha = ""
    modules_sha = ""
    modules_short_sha = ""

    for mf in sorted(meta_files):
        env_data = parse_env_file(mf)
        v = env_data.get("VARIANT")
        if v:
            variants_info[v] = env_data
        if not kernel_sha and env_data.get("KERNEL_SHA"):
            kernel_sha = env_data["KERNEL_SHA"]
            kernel_short_sha = env_data.get("KERNEL_SHORT_SHA", kernel_sha[:7])
        if not modules_sha and env_data.get("MODULES_SHA"):
            modules_sha = env_data["MODULES_SHA"]
            modules_short_sha = env_data.get("MODULES_SHORT_SHA", modules_sha[:7])
        if env_data.get("SUBLEVEL"):
            sublevel = env_data["SUBLEVEL"]

    # Format kernel source links with HEAD commit
    if kernel_sha:
        k_commit_url = f"{k_repo}/commit/{kernel_sha}"
        k_ref_md = f"[{k_repo}]({k_repo}) (`{k_branch}`) @ [`{kernel_short_sha}`]({k_commit_url})"
    else:
        k_ref_md = f"[{k_repo}]({k_repo}) (`{k_branch}`)"

    if modules_sha:
        m_commit_url = f"{m_repo}/commit/{modules_sha}"
        m_ref_md = f"[{m_repo}]({m_repo}) (`{m_branch}`) @ [`{modules_short_sha}`]({m_commit_url})"
    else:
        m_ref_md = f"[{m_repo}]({m_repo}) (`{m_branch}`)"

    rom_dir_url = f"https://files.gauravbuilds.xyz/release/aston/{rom}/"

    # Detailed specifications for boot images
    boot_items = {
        "vanilla": {
            "file": "boot.img",
            "title": "Clean Stock ROM Kernel",
            "desc": "Repacked base ROM boot.img with clean compiled Image (no root modifications)",
            "root_info": "None (Stock Unrooted)",
            "susfs_info": "None",
            "manager_info": "N/A"
        },
        "ksun": {
            "file": "boot-ksun.img",
            "title": "KernelSU-Next",
            "desc": "KernelSU-Next official dev branch",
            "root_info": "KernelSU-Next (branch `dev`)",
            "susfs_info": "None",
            "manager_info": "KernelSU-Next Manager APK"
        },
        "ksun-susfs": {
            "file": "boot-ksun-susfs.img",
            "title": "KernelSU-Next + SuSFS",
            "desc": "KernelSU-Next (pershoot dev-susfs) with full SuSFS v1.5.5 kernel patches",
            "root_info": "KernelSU-Next (pershoot branch `dev-susfs`)",
            "susfs_info": "SuSFS v1.5.5 (`gki-android13-5.15`)",
            "manager_info": "KernelSU-Next Manager APK + SuSFS Manager APK"
        },
        "resukisu-susfs": {
            "file": "boot-resuki-susfs.img",
            "title": "BakaSU (ReSukiSU) + SuSFS",
            "desc": "BakaSU / ReSukiSU (main branch) with full SuSFS v1.5.5 kernel patches",
            "root_info": "BakaSU / ReSukiSU (branch `main`)",
            "susfs_info": "SuSFS v1.5.5 (`gki-android13-5.15`)",
            "manager_info": "KernelSU Manager / KernelSU-Next Manager / BakaSU Manager + SuSFS Manager"
        }
    }

    boot_lines = []
    for var, spec in boot_items.items():
        img_name = spec["file"]
        title = spec["title"]
        root_info = spec["root_info"]
        susfs_info = spec["susfs_info"]
        manager_info = spec["manager_info"]
        desc = spec["desc"]

        if var in variants_info:
            vdata = variants_info[var]
            if vdata.get("ROOT_DESC"):
                desc = vdata["ROOT_DESC"]
            if vdata.get("ROOT_VERSION"):
                root_info += f" @ `{vdata['ROOT_VERSION']}`"
            if vdata.get("SUSFS_VERSION"):
                susfs_info = vdata["SUSFS_VERSION"]

        boot_lines.append(f"""### 💿 `{img_name}` ({title})
- **Description:** {desc}
- **Root Solution:** {root_info}
- **SuSFS Version:** {susfs_info}
- **Compatible Managers:** {manager_info}
""")

    boot_imgs_md = "\n".join(boot_lines)

    md = f"""# 🚀 {rom} OnePlus 12R (Aston / SM8550) Kernel Release

### 📱 Target ROM & Build Information
- **Target ROM Package:** [`{latest_rom_zip}`]({rom_dir_url})
- **Base `boot.img` Source:** [{base_url}]({base_url})
- **Device:** OnePlus 12R (`aston` / Qualcomm Snapdragon 8 Gen 2 / `sm8550`)
- **Linux Kernel Version:** `5.15.{sublevel}`
- **Build Timestamp:** `{date_display}`
- **Compiler:** `{clang_ver}` (AOSP Clang with LLVM LLD)

---

### 📦 Available Boot Images & Root Solutions
{boot_imgs_md}

---

### 🔗 Source References & Commit SHAs
- **Kernel Tree:** {k_ref_md}
- **Modules Tree:** {m_ref_md}
- **ROM Directory:** [{rom_dir_url}]({rom_dir_url})
- **KernelSU-Next:** [KernelSU-Next/KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next) (`dev`)
- **KernelSU-Next (SuSFS):** [pershoot/KernelSU-Next](https://github.com/pershoot/KernelSU-Next/tree/dev-susfs) (`dev-susfs`)
- **SuSFS (simonpunk):** [simonpunk/susfs4ksu](https://gitlab.com/simonpunk/susfs4ksu) (`gki-android13-5.15`)
- **BakaSU (ReSukiSU):** [Baka-SU/BakaSU](https://github.com/Baka-SU/BakaSU) (`main`)

---

### ⚡ Flashing Instructions
1. Download your preferred `.img` from the assets below.
2. Reboot your device into bootloader mode:
```bash
adb reboot bootloader
```
3. Flash the boot image:
```bash
fastboot flash boot <chosen_boot_image>.img
fastboot reboot
```

---

### 🛡️ SHA256 Checksums
```
{checksums}
```
"""
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"==> Generated {out_file} successfully.")

if __name__ == '__main__':
    main()
