#!/usr/bin/env python3
import sys

def main():
    print("==> Resolving OnePlus SM8550 trace hook conflict in fs/namespace.c...")
    with open('fs/namespace.c', 'r', encoding='utf-8') as f:
        c = f.read()

    t1 = '#include <linux/mnt_idmapping.h>'
    r1 = '''#include <linux/mnt_idmapping.h>
#ifdef CONFIG_KSU_SUSFS
#include <linux/susfs_def.h>
#endif // #ifdef CONFIG_KSU_SUSFS'''

    t2 = '/* Maximum number of mounts in a mount namespace */'
    r2 = '''#ifdef CONFIG_KSU_SUSFS_SUS_MOUNT
extern bool susfs_is_current_ksu_domain(void);
extern struct static_key_true susfs_is_sdcard_android_data_not_decrypted;

#define CL_COPY_MNT_NS BIT(25) /* used by copy_mnt_ns() */
#endif // #ifdef CONFIG_KSU_SUSFS_SUS_MOUNT

/* Maximum number of mounts in a mount namespace */'''

    if t1 in c and '#include <linux/susfs_def.h>' not in c:
        c = c.replace(t1, r1, 1)

    if t2 in c and 'susfs_is_current_ksu_domain' not in c:
        c = c.replace(t2, r2, 1)

    with open('fs/namespace.c', 'w', encoding='utf-8') as f:
        f.write(c)

    print("==> Adapting SuSFS patch for OnePlus GKI 5.15...")
    patch_in = sys.argv[1] if len(sys.argv) > 1 else '/tmp/susfs/kernel_patches/50_add_susfs_in_gki-android14-5.15.patch'
    patch_out = sys.argv[2] if len(sys.argv) > 2 else 'susfs.patch'

    with open(patch_in, 'r', encoding='utf-8', errors='ignore') as f:
        p = f.read()

    idx = p.find('diff --git a/fs/namespace.c ')
    if idx != -1:
        h1 = p.find('@@ -32,10 +32,20 @@', idx)
        h2 = p.find('@@ -144,6 +154,10 @@', idx)
        if h1 != -1 and h2 != -1:
            p = p[:h1] + p[h2:]

    with open(patch_out, 'w', encoding='utf-8') as f:
        f.write(p)

    print("==> Successfully prepared SuSFS patch.")

if __name__ == '__main__':
    main()
