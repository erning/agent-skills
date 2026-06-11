---
name: git-crypt
description: "How to use git-crypt for transparent encryption of files in Git repositories. Use this skill whenever the user wants to encrypt files in a Git repo, set up git-crypt, manage encrypted secrets alongside code, share encrypted repo access via GPG or symmetric keys, recover from plaintext secrets already committed to Git history, or troubleshoot git-crypt issues. Also use it when the user mentions protecting secrets in Git, .gitattributes encryption filters, selectively encrypting repository files, leaked secrets, exported git-crypt keys, or key handling safety."
---

# git-crypt: Transparent File Encryption in Git

git-crypt lets you store encrypted files in a Git repository. Encryption and decryption happen transparently — encrypted files look like normal files during day-to-day work, but are stored as ciphertext in the repo. People without the key can still clone and work on unencrypted parts of the repo.

## When to use git-crypt

git-crypt is ideal for repos that are **mostly public** with a **few sensitive files** (API keys, credentials, config secrets). If the entire repo needs to be encrypted, recommend `git-remote-gcrypt` instead.

## Safety First

Start by deciding whether the user is protecting future commits or responding
to an existing leak.

- If secrets have already been committed or pushed in plaintext, say clearly
  that git-crypt only encrypts future repository contents. It does not erase
  plaintext already present in Git history, remote clones, forks, CI logs, or
  downloaded archives.
- For already-exposed credentials, advise rotating or revoking the secrets
  before relying on repository cleanup. Treat history rewriting as cleanup, not
  containment.
- Do not print, invent, or ask the user to paste real secrets or exported
  git-crypt key material into the conversation.
- Never commit an exported git-crypt key, private GPG key, `.env` secret, or
  decrypted secret backup. Share key material out of band through a password
  manager or another secure channel.
- Before committing sensitive files, verify `.gitattributes` is already
  committed and run `git-crypt status` to confirm the intended files are
  encrypted.

## Quick Start

### 0. Check for existing plaintext secrets

Before adding git-crypt rules, inspect whether the files already exist in Git:

```bash
git ls-files .env config/secrets.yml credentials/
git log --all -- .env config/secrets.yml credentials/
```

If any sensitive file is already tracked or appears in history, follow
[Adding git-crypt to an existing repo](#adding-git-crypt-to-an-existing-repo)
instead of treating this as a clean setup.

### 1. Initialize git-crypt in a repo

```bash
cd my-repo
git-crypt init
```

This generates a symmetric encryption key stored inside `.git/git-crypt/`.

### 2. Specify which files to encrypt

Create or edit `.gitattributes` **before adding any sensitive files**:

```gitattributes
# Encrypt specific files
secrets.yml filter=git-crypt diff=git-crypt
.env filter=git-crypt diff=git-crypt

# Encrypt by pattern
*.key filter=git-crypt diff=git-crypt
*.pem filter=git-crypt diff=git-crypt

# Encrypt an entire directory (use ** not *)
secrets/** filter=git-crypt diff=git-crypt

# IMPORTANT: never encrypt .gitattributes itself
.gitattributes !filter !diff
```

**Critical rules for .gitattributes:**
- The `.gitattributes` file MUST be committed before adding sensitive files, otherwise files get committed in plaintext and remain in Git history forever
- Never encrypt `.gitattributes`, `.gitignore`, or `.gitmodules`
- To encrypt a directory recursively, use `dir/**` (not `dir/*` — the single-star form won't match files in subdirectories)
- Add `.gitattributes !filter !diff` to explicitly exclude it from encryption

### 3. Share access

**Option A — GPG keys (recommended for teams):**

```bash
git-crypt add-gpg-user user@example.com
```

This encrypts the repo key with the user's GPG public key and auto-commits the result into `.git-crypt/`. The recipient unlocks with:

```bash
git-crypt unlock
```

**Option B — Symmetric key (simpler, for small teams):**

```bash
# Export the key file
git-crypt export-key /path/to/git-crypt-key

# Share the key file securely (NOT via the repo itself!)
# The recipient unlocks with:
git-crypt unlock /path/to/git-crypt-key
```

The key file must be shared out-of-band (e.g., password manager, encrypted messaging). Never commit the exported key to the repo.

## Key Handling Rules

- Prefer GPG access for teams because each user unlocks the repo with their own
  key and access grants are recorded in `.git-crypt/`.
- Use exported symmetric keys only when there is a clear secure sharing channel
  and a plan for storage.
- Store exported key files outside the repository. Add local filenames such as
  `git-crypt-key` or `*.git-crypt-key` to `.gitignore` if they might be created
  near the repo.
- If a symmetric key file or private GPG key was committed or shared in an
  unsafe place, treat the encrypted contents as exposed. Rotate the protected
  secrets and re-key the repository where possible.

## Command Reference

### `git-crypt init`

Generate a new encryption key and prepare the repo.

```bash
git-crypt init                    # Initialize with default key
git-crypt init -k KEYNAME         # Initialize an alternative named key
```

### `git-crypt unlock`

Decrypt the repo so encrypted files become readable.

```bash
git-crypt unlock                  # Unlock using GPG (your key must be in the repo)
git-crypt unlock /path/to/key     # Unlock using a symmetric key file
```

### `git-crypt lock`

Re-encrypt files in the working tree and de-configure git-crypt filters. Useful before sharing the repo directory with someone who shouldn't see secrets.

```bash
git-crypt lock                    # Lock the default key
git-crypt lock -k KEYNAME         # Lock a specific named key
git-crypt lock -a                 # Lock all keys
git-crypt lock -f                 # Force lock even with uncommitted changes
```

**Warning:** `lock -f` can discard uncommitted changes to encrypted files. Always commit first.

### `git-crypt status`

Show which files are encrypted and which aren't.

```bash
git-crypt status                  # Show all files and their encryption status
git-crypt status -e               # Show only encrypted files
git-crypt status -u               # Show only unencrypted files
git-crypt status -f               # Fix: encrypt files that should be encrypted but aren't
```

`status -f` is the rescue command when files were committed before `.gitattributes` was in place.

### `git-crypt add-gpg-user`

Grant a GPG user access to the repo's encrypted files.

```bash
git-crypt add-gpg-user USER_ID              # Add for default key
git-crypt add-gpg-user -k KEYNAME USER_ID   # Add for a specific named key
git-crypt add-gpg-user -n USER_ID           # Add without auto-committing
git-crypt add-gpg-user --trusted USER_ID    # Skip GPG trust verification
```

`USER_ID` can be a GPG key ID, fingerprint, or email address.

### `git-crypt export-key`

Export the symmetric key to a file for out-of-band sharing.

```bash
git-crypt export-key /path/to/keyfile           # Export default key
git-crypt export-key -k KEYNAME /path/to/keyfile # Export a named key
git-crypt export-key -                           # Export to stdout
```

## Multiple Keys

Use named keys when different people need access to different sets of secrets (e.g., the frontend team sees frontend secrets, the backend team sees backend secrets).

```bash
# Create named keys
git-crypt init -k frontend
git-crypt init -k backend
```

In `.gitattributes`, reference the key name in the filter:

```gitattributes
frontend/secrets/** filter=git-crypt-frontend diff=git-crypt-frontend
backend/secrets/**  filter=git-crypt-backend  diff=git-crypt-backend
```

Grant access per key:

```bash
git-crypt add-gpg-user -k frontend frontend-dev@example.com
git-crypt add-gpg-user -k backend  backend-dev@example.com
```

`git-crypt unlock` automatically detects which key a user has access to.

## Common Workflows

### Setting up a new project with secrets

```bash
git init my-project && cd my-project
git-crypt init

# Define what to encrypt FIRST
cat > .gitattributes << 'EOF'
.env filter=git-crypt diff=git-crypt
config/secrets.yml filter=git-crypt diff=git-crypt
credentials/** filter=git-crypt diff=git-crypt
.gitattributes !filter !diff
EOF

git add .gitattributes
git commit -m "Configure git-crypt encryption rules"

# NOW add secret files
echo "API_KEY=abc123" > .env
git add .env
git commit -m "Add encrypted environment config"
```

### Adding git-crypt to an existing repo

If secret files already exist unencrypted in the repo, they're already in Git
history. Handle this as an incident:

1. Rotate or revoke the exposed credentials first.
2. Add `.gitattributes` rules for the files or directories that should be
   encrypted, using `dir/**` for recursive directories.
3. Commit `.gitattributes`.
4. Run `git-crypt status -f` to encrypt tracked files going forward.
5. Verify the result with `git-crypt status` and `git show HEAD:path | file -`.
6. Clean historical plaintext with `git filter-repo` or BFG Repo-Cleaner if the
   repository history must be preserved without the leaked content.
7. Coordinate force-pushes and fresh clones with collaborators after rewriting
   history.

Do not present history cleanup as a substitute for credential rotation. Copies
may still exist in forks, local clones, caches, CI logs, package artifacts, or
other places outside the rewritten repository.

### Checking if files are actually encrypted

```bash
# Show encryption status of all files
git-crypt status

# Verify a specific file is encrypted in the repo
git show HEAD:path/to/secret | file -
# Should show "data" (binary), not readable text
```

### Generating a diff for encrypted files

Normal `git diff` won't work on encrypted files for patching. Use:

```bash
git diff --no-textconv --binary
```

## Troubleshooting

### "Error: this repository has not been set up with git-crypt"
Run `git-crypt init` first, or if the repo was already initialized by someone else, run `git-crypt unlock` with the appropriate key.

### Files committed in plaintext before .gitattributes was set up
Run `git-crypt status -f` to encrypt them going forward. The plaintext versions
remain in history. Rotate the exposed secrets, then use `git filter-repo` or BFG
Repo-Cleaner if the repository history must be scrubbed.

### "Error: working copy is not clean"
Commit or stash changes before running `git-crypt lock`. Or use `git-crypt lock -f` if you're sure (this can discard uncommitted changes to encrypted files).

### GUI clients showing garbled content
Some Git GUIs (notably Atlassian SourceTree) don't properly invoke git-crypt filters. The files may appear as binary garbage or get committed unencrypted. Use the command line for repos with git-crypt.

## Important Limitations

- **No key revocation or rotation.** Once someone has had access, they can decrypt all historical data. Removing a GPG user from `.git-crypt/` doesn't revoke their access to past commits.
- **Metadata is not encrypted.** Filenames, commit messages, branch names, and symlink targets are always visible in plaintext.
- **No compression.** Encrypted files can't be delta-compressed by Git, so every change stores a full copy.
- **Deterministic encryption.** Identical files encrypt to identical ciphertext. This is by design (AES-256-CTR with HMAC-SHA1 synthetic IV) — it's secure against chosen-plaintext attacks, but it does leak whether two files are identical.
- **Repository integrity.** An attacker with write access to the repo could modify `.gitattributes` to silently disable encryption on future commits. Protect repo write access.

## Installation

```bash
# macOS
brew install git-crypt

# Debian/Ubuntu
apt install git-crypt

# From source
make && make install
```

Requires Git 1.7.2+ (1.8.5+ recommended) and OpenSSL.
