# Configure and verify encryption

Inspect the requested paths and existing git-crypt configuration before
changing rules. Use path-scoped history and status commands without printing
secrets. Tracked files may already be encrypted; distinguish that from
committed plaintext.

## New rules

Initialize with `git-crypt init` only if the repository has no existing key
setup. For a clone of an initialized repository, unlock it with an existing
key instead.

Example `.gitattributes` rules; adapt the paths to the user's scope:

```gitattributes
.env filter=git-crypt diff=git-crypt
config/secrets.yml filter=git-crypt diff=git-crypt
credentials/** filter=git-crypt diff=git-crypt
.gitattributes !filter !diff
```

Keep Git control files unencrypted even when broader patterns would match
them. Rules and filters must be active when sensitive files are added to the
index. The rules and encrypted files can be part of the same commit:

```bash
git add .gitattributes
git add -- .env config/secrets.yml
git-crypt status
```

Only stage and commit when the surrounding task authorizes those operations.
An explanation request needs commands and guidance, not repository mutations.

## Verify the correct version

`git-crypt status` checks encryption configuration and detects unencrypted
stored blobs. Inspect the index when validating staged changes. `HEAD`
describes the last commit and does not include uncommitted repairs.

The following checks report only whether a stored blob has git-crypt's header;
they do not print the contents. Use them alongside a successful
`git-crypt status`, not as proof of key access or ciphertext authenticity.
Substitute the actual path.

```bash
# Staged version
git cat-file blob :.env | python3 -c 'import sys; ok = sys.stdin.buffer.read().startswith(b"\0GITCRYPT\0"); print("git-crypt header:", "yes" if ok else "no"); sys.exit(0 if ok else 1)'

# Committed version, after the requested commit
git cat-file blob HEAD:.env | python3 -c 'import sys; ok = sys.stdin.buffer.read().startswith(b"\0GITCRYPT\0"); print("git-crypt header:", "yes" if ok else "no"); sys.exit(0 if ok else 1)'
```

`file` reporting generic binary data is not sufficient evidence of encryption.

## Existing plaintext

Determine whether plaintext is only in the work tree, staged, committed, or
already shared. If credentials were exposed, recommend rotation or revocation.

After initializing or unlocking git-crypt and configuring the rules, run
`git-crypt status -f` to stage encrypted replacements for files needing
repair. This command modifies the index; it does not commit the replacements.
Review its affected paths and be aware that it may repair other matching files
in the repo. If that would exceed the task's scope, reapply the clean filter
only to the requested tracked files with `git add --renormalize -- <paths>`
after enabling the rules. Ordinary `git add` can leave an unchanged tracked
file untouched.

Verify the staged version, commit if requested, and then verify the committed
version. Historical plaintext remains even when the new commit is encrypted.

For requested history cleanup, choose a tool such as `git filter-repo` or BFG
Repo-Cleaner and prepare the affected refs and paths before rewriting. Obtain
any missing authorization for history changes and force-pushes. Copies in
clones, forks, caches, CI logs, and archives may remain outside that cleanup.
