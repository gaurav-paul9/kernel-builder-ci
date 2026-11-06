#!/usr/bin/env python3
import sys
import os

def patch_bakasu(kernel_dir):
    print(f"==> Patching BakaSU for SuSFS compatibility in {kernel_dir}...")

    # 1. Patch susfs_compat.mk
    for mk_rel in ["KernelSU/kernel/tools/susfs_compat.mk", "drivers/kernelsu/tools/susfs_compat.mk"]:
        mk_path = os.path.join(kernel_dir, mk_rel)
        if os.path.isfile(mk_path):
            with open(mk_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            new_lines = [l for l in lines if not any(k in l for k in [
                "Please wait susfs update",
                "has NOT update with latest KernelSU source",
                "Please wait simonpunk update"
            ])]
            # Explicitly force SuSFS SELinux hide flags
            new_lines.append("\n# Enforce SuSFS SELinux hide and direct fd compat\n")
            new_lines.append("ccflags-y += -DKSU_COMPAT_HAS_SUSFS_FEATURE_SELINUX_HIDE\n")
            new_lines.append("ccflags-y += -DKSU_COMPAT_HAS_SUSFS_INSTALL_SU_FD_DIRECT_CALL\n")
            with open(mk_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"[patch_bakasu] Cleaned and enforced flags in {mk_path}")

    # 2. Patch Kbuild to guarantee preinit objects and manager signature support
    for kb_rel in ["KernelSU/kernel/Kbuild", "drivers/kernelsu/Kbuild"]:
        kb_path = os.path.join(kernel_dir, kb_rel)
        if os.path.isfile(kb_path):
            with open(kb_path, "r", encoding="utf-8", errors="ignore") as f:
                kb_content = f.read()

            # Ensure preinit is included
            if "preinit/preinit.o" not in kb_content:
                kb_content += "\n# Force preinit runner objects for SuSFS\n"
                kb_content += "kernelsu-objs += preinit/preinit.o\n"
                kb_content += "kernelsu-objs += preinit/blob.o\n"

            # Ensure code generation is included
            if "code_generation.mk" not in kb_content:
                kb_content += "\ninclude $(KSU_SRC)/tools/code_generation/code_generation.mk\n"

            # Set custom manager signature to support KernelSU-Next Manager
            if "EXPECTED_SIZE" not in kb_content:
                kb_content += "\n# Support KernelSU-Next Manager APK v2 signature\n"
                kb_content += "KSU_EXPECTED_SIZE := 0x3e6\n"
                kb_content += "KSU_EXPECTED_HASH := 79e590113c4c4c0c222978e413a5faa801666957b1212a328e46c00c69821bf7\n"
                kb_content += "ccflags-y += -DEXPECTED_SIZE=$(KSU_EXPECTED_SIZE) -DEXPECTED_HASH=\\\"$(KSU_EXPECTED_HASH)\\\"\n"

            with open(kb_path, "w", encoding="utf-8") as f:
                f.write(kb_content)
            print(f"[patch_bakasu] Updated Kbuild at {kb_path}")

    # 3. Patch selinux_hide.h for fake_state
    for h_rel in ["KernelSU/kernel/feature/selinux_hide.h", "drivers/kernelsu/feature/selinux_hide.h"]:
        h_path = os.path.join(kernel_dir, h_rel)
        if os.path.isfile(h_path):
            with open(h_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if "extern struct selinux_state fake_state;" not in content:
                content += "\nstruct selinux_state;\nextern struct selinux_state fake_state;\n"
                with open(h_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"[patch_bakasu] Added fake_state extern to {h_path}")

    # 4. Patch selinux_hide.c for fake_state definition and initialization
    for c_rel in ["KernelSU/kernel/feature/selinux_hide.c", "drivers/kernelsu/feature/selinux_hide.c"]:
        c_path = os.path.join(kernel_dir, c_rel)
        if os.path.isfile(c_path):
            with open(c_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            modified = False
            if "struct selinux_state fake_state;" not in content:
                marker = '#include "selinux_hide.h"'
                if marker in content:
                    content = content.replace(marker, marker + "\nstruct selinux_state fake_state;\n", 1)
                    modified = True
                else:
                    content = "struct selinux_state fake_state;\n" + content
                    modified = True

            hook_marker = 'pr_info("selinux_hide: init selinux hide\\n");'
            assignment = '\n    fake_state.initialized = true;\n    fake_state.policy = backup_sepolicy;\n'
            if hook_marker in content and "fake_state.policy = backup_sepolicy;" not in content:
                content = content.replace(hook_marker, hook_marker + assignment, 1)
                modified = True

            if modified:
                with open(c_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"[patch_bakasu] Injected fake_state definition and hook into {c_path}")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    patch_bakasu(target_dir)
