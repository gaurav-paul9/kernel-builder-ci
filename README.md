# OnePlus 12R (Aston / SM8550) Kernel Builder CI

Automated GitHub Actions CI repository to compile custom Linux kernels for the **OnePlus 12R (`aston`)** (Qualcomm SM8550 Snapdragon 8 Gen 2) and automatically pack them into flashable Android `boot.img` files for **Yaap** and **Lunaris** ROMs.

Instead of producing AnyKernel3 flashable `.zip` files, this CI downloads the official base Android Boot Header v4 `boot.img` from the ROM release servers, unpacks it using `magiskboot`, replaces the kernel payload with the freshly compiled kernel `Image`, and releases ready-to-flash `.img` files via GitHub Releases.

---

## 🚀 Features

- **Multi-ROM Support**:
  - **Yaap** (Android 16 / seventeen)
  - **Lunaris** (Android 16 / seventeen)
- **4 Boot Image Variants** per build:
  1. `boot.img` — Clean / Vanilla ROM kernel.
  2. `boot-ksun.img` — [KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next) (dev branch).
  3. `boot-ksun-susfs.img` — [KernelSU-Next (dev-susfs)](https://github.com/pershoot/KernelSU-Next/tree/dev-susfs) + [SuSFS v1.5.x](https://gitlab.com/simonpunk/susfs4ksu).
  4. `boot-resuki-susfs.img` — [BakaSU (ReSukiSU)](https://github.com/Baka-SU/BakaSU) + [SuSFS v1.5.x](https://gitlab.com/simonpunk/susfs4ksu).
- **Parallel Matrix Execution**: All 4 variants build concurrently on separate GitHub Actions runners in ~12–15 minutes without running out of disk space.
- **Automated magiskboot Repack**: Downloads official base `boot.img` from ROM file mirrors, unpacks `kernel`, swaps with compiled ARM64 `Image`, and repacks.
- **Automated GitHub Releases**: Generates releases with date/timestamp, commit SHAs for kernel, modules, devicetrees, and SHA256 checksums for all `.img` files.

---

## 🛠️ How to Trigger a Build

1. Go to the **Actions** tab in this repository.
2. Select **OnePlus 12R (Aston) Kernel CI** from the left sidebar.
3. Click **Run workflow**.
4. Configure options:
   - **Target ROM**: Choose `Yaap` or `Lunaris`.
   - **Root variant to build**: Select `all` (default) or build a single variant (`vanilla`, `ksun`, `ksun-susfs`, `resukisu-susfs`).
   - **AOSP Clang version**: `clang-r563880c` (recommended for Android 16/QPR2) or older versions.
   - **Kernel Branch**: (Optional) Override branch (defaults to `seventeen`).
   - **Custom base boot.img URL**: (Optional) Custom mirror URL for base `boot.img`.
5. Click **Run workflow**.

---

## 📲 How to Flash

Once the GitHub Release is generated, download your desired `.img` file and flash it via Fastboot:

```bash
# 1. Reboot your OnePlus 12R into Fastboot mode
adb reboot bootloader

# 2. Flash the chosen boot image
fastboot flash boot boot-ksun-susfs.img

# 3. Reboot into system
fastboot reboot
```

> **Note**: For devices with A/B slot partitions, `fastboot flash boot <image>` flashes the active slot automatically.

---

## 🔗 Upstream Sources & References

| Component | Repository / Source | Branch |
| :--- | :--- | :--- |
| **Yaap Kernel** | [gaurav-paul9/android_kernel_oneplus_sm8550](https://github.com/gaurav-paul9/android_kernel_oneplus_sm8550) | `seventeen` |
| **Yaap Modules** | [gaurav-paul9/android_kernel_oneplus_sm8550-modules](https://github.com/gaurav-paul9/android_kernel_oneplus_sm8550-modules) | `seventeen` |
| **Yaap Base boot.img** | [files.gauravbuilds.xyz/release/aston/Yaap/imgs-17/boot.img](https://files.gauravbuilds.xyz/release/aston/Yaap/imgs-17/boot.img) | — |
| **Lunaris Kernel** | [OnePlus12R-development/android_kernel_oneplus_sm8550](https://github.com/OnePlus12R-development/android_kernel_oneplus_sm8550) | `seventeen` |
| **Lunaris Modules** | [gaurav-paul9/android_kernel_oneplus_sm8550-modules](https://github.com/gaurav-paul9/android_kernel_oneplus_sm8550-modules) | `lunaris` |
| **Lunaris Base boot.img**| [files.gauravbuilds.xyz/release/aston/Lunaris/imgs/boot.img](https://files.gauravbuilds.xyz/release/aston/Lunaris/imgs/boot.img) | — |
| **KernelSU-Next** | [KernelSU-Next/KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next) | `dev` |
| **KernelSU-Next (SuSFS)**| [pershoot/KernelSU-Next](https://github.com/pershoot/KernelSU-Next) | `dev-susfs` |
| **SuSFS** | [simonpunk/susfs4ksu](https://gitlab.com/simonpunk/susfs4ksu) | `gki-android14-5.15` |
| **BakaSU** | [Baka-SU/BakaSU](https://github.com/Baka-SU/BakaSU) | `main` |
| **Magiskboot** | [topjohnwu/Magisk](https://github.com/topjohnwu/Magisk) | `v28.1` |

---

## 📢 Telegram Channel Auto-Posting Setup

The workflow includes automated release broadcasting to a Telegram channel upon successful completion:

1. Create a bot using [@BotFather](https://t.me/BotFather) on Telegram and copy the Bot Token.
2. Create your Telegram Channel / Group and add your bot as an **Administrator** with "Post Messages" permission.
3. In this GitHub repository, navigate to **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions** and add two Repository Secrets:
   - `TELEGRAM_BOT_TOKEN`: The token from BotFather (e.g., `123456789:ABCdefGHI...`)
   - `TELEGRAM_CHAT_ID`: The channel ID (e.g., `@your_channel_name` or numeric `-100xxxxxxxxxx`)
4. Subsequent builds will automatically publish an announcement with release notes, commit SHAs, and download links directly to your channel!

