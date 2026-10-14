#!/usr/bin/env python3
import sys
import os

def main():
    if len(sys.argv) < 10:
        print("Usage: generate_release_notes.py <rom> <sublevel> <date_display> <clang_ver> <k_repo> <k_branch> <m_repo> <m_branch> <base_url> [out_file]")
        sys.exit(1)

    rom = sys.argv[1]
    sublevel = sys.argv[2]
    date_display = sys.argv[3]
    clang_ver = sys.argv[4]
    k_repo = sys.argv[5]
    k_branch = sys.argv[6]
    m_repo = sys.argv[7]
    m_branch = sys.argv[8]
    base_url = sys.argv[9]
    out_file = sys.argv[10] if len(sys.argv) > 10 else "release_notes.md"

    checksums = ""
    if os.path.exists("SHA256SUMS.txt"):
        with open("SHA256SUMS.txt", "r", encoding="utf-8") as f:
            checksums = f.read().strip()

    md = f"""# {rom} OnePlus 12R (Aston / SM8550) Kernel Release

- **ROM:** {rom}
- **Device:** OnePlus 12R (Aston) [SM8550]
- **Linux Kernel Version:** 5.15.{sublevel}
- **Build Timestamp:** {date_display}
- **AOSP Clang Version:** {clang_ver}

---

### 📦 Available Boot Images
- `boot.img` - Stock / Vanilla ROM kernel (repacked into base ROM boot.img)
- `boot-ksun.img` - KernelSU-Next (dev branch)
- `boot-ksun-susfs.img` - KernelSU-Next (dev-susfs) + SuSFS v1.5.x
- `boot-resuki-susfs.img` - BakaSU (ReSukiSU) + SuSFS v1.5.x

---

### 🔗 Source References
- **Kernel Tree:** [{k_repo}]({k_repo}) (`{k_branch}`)
- **Modules Tree:** [{m_repo}]({m_repo}) (`{m_branch}`)
- **Base boot.img Source:** [{base_url}]({base_url})
- **KernelSU-Next:** [KernelSU-Next/KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next)
- **KernelSU-Next (SuSFS):** [pershoot/KernelSU-Next](https://github.com/pershoot/KernelSU-Next/tree/dev-susfs)
- **SuSFS:** [simonpunk/susfs4ksu](https://gitlab.com/simonpunk/susfs4ksu)
- **BakaSU:** [Baka-SU/BakaSU](https://github.com/Baka-SU/BakaSU)

---

### ⚡ Installation Instructions
Reboot device into fastboot / bootloader mode:
```bash
adb reboot bootloader
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
