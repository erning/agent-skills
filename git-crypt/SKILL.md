---
name: git-crypt
description: >-
  Configure file encryption with git-crypt, manage repository key access, or
  troubleshoot git-crypt. Use for Git file-encryption tasks; a generic secret
  leak or credential-storage question alone does not trigger this skill.
---

# git-crypt

Use git-crypt for selected files that should remain readable in an unlocked
work tree and encrypted in Git. Follow the user's chosen tool and file scope.

## Task guidance

Read only the reference needed for the requested operation:

- New encryption rules, tracked plaintext, or checking stored contents:
  [references/setup.md](references/setup.md).
- GPG access, symmetric-key export, or separate access groups:
  [references/access.md](references/access.md).
- Locking, unlocking, errors, or encrypted patches:
  [references/troubleshooting.md](references/troubleshooting.md).

For simple explanations, the constraints below may be enough. A setup request
does not imply permission to grant access, rewrite history, or force-push.

## Constraints

- Configure the encryption filter and matching `.gitattributes` rules before
  adding sensitive files to the index. Track `.gitattributes`; a separate
  earlier commit is optional. Verify encryption in the index before
  committing, and in the committed blob after a requested commit.
- Use `dir/**` for recursive rules. Keep `.gitattributes`, `.gitignore`, and
  `.gitmodules` unencrypted.
- Keep exported repository keys and private GPG keys outside the repository.
  Do not print keys or secret file contents. Sensitive application files such
  as `.env` may be committed only after their stored form is verified as
  encrypted.
- Encrypting current files does not remove historical plaintext. If
  credentials were exposed, advise rotation or revocation; history cleanup is
  a separate operation. A tracked file is not, by itself, evidence of a leak.
- Access cannot be revoked from someone who already has the key. Removing a
  GPG grant does not invalidate their key or access to historical ciphertext.
- Filenames and other Git metadata remain visible. Encryption reveals file
  lengths and equality; repository write access can be used to disable
  filters.

Complete the requested operation and verify its stored result. Report staged
changes as staged, and do not claim that history or remote copies were cleaned
without performing and checking that work.

## Upstream reference

Use the installed version's `git-crypt help` for options and the
[upstream README](https://github.com/AGWA/git-crypt#using-git-crypt) for tool
behavior and limitations.
