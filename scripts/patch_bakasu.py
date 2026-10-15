#!/usr/bin/env python3
import sys
import os

def patch_bakasu(kernel_dir):
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
            with open(mk_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"[patch_bakasu] Cleaned susfs_compat.mk at {mk_path}")

    # 2. Patch selinux_hide.h
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

    # 3. Patch selinux_hide.c
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
