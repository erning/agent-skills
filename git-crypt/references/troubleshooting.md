# Troubleshooting git-crypt

Use `git-crypt status` and inspect configuration for the affected paths. Avoid
printing decrypted diffs, work-tree secrets, or exported keys during
diagnosis.

| Symptom | Action |
| --- | --- |
| Repository not set up locally | For an existing encrypted repository, unlock with its existing key. Initialize only a new encryption setup. |
| Files marked for encryption are stored as plaintext | Read [setup.md](setup.md), enable the rules and filters, stage encrypted replacements, and verify the index. |
| Working copy is not clean when locking | Preserve pending changes by a task-appropriate commit, stash, or protected backup. `lock -f` can discard changes and is not an automatic retry. |
| A GUI shows binary content or misses filters | Recheck status with the Git CLI and inspect the relevant version without exposing contents. |
| A recipient cannot unlock | Check their GPG identity or symmetric key location and which repository key was granted; do not generate a new unrelated key. |

## Locking and unlocking

```bash
git-crypt lock
git-crypt lock -k KEYNAME
git-crypt lock -a
git-crypt unlock
git-crypt unlock /secure/location/repository.key
```

Locking restores encrypted work-tree files and disables the local filters.
Ensure changes are preserved before locking, and check the result for the
requested key or file scope.

## Encrypted patches

For a patch suitable for Git's patch machinery, generate binary ciphertext
diffs:

```bash
git diff --no-textconv --binary
```

Ordinary text-converted diffs can show decrypted content and are unsuitable
for `git apply` against stored ciphertext. Handle plaintext patches only in an
appropriate unlocked work tree with a tool that understands the target
contents.

## Installation

If installation is part of the task, use the platform's package manager, such
as `brew install git-crypt` or `apt install git-crypt`. Follow the
[upstream build instructions](https://github.com/AGWA/git-crypt/blob/master/INSTALL.md)
when building from source.
