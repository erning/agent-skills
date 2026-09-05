# Key access

Select GPG grants or symmetric-key sharing according to the user's workflow.
Confirm the intended recipient and key identity before granting access.

## GPG

```bash
git-crypt add-gpg-user USER_ID
```

`USER_ID` can be a fingerprint or another unambiguous GPG identity. The
command stores an encrypted repository key under `.git-crypt/` and commits it
by default. Use `-n` when access should be prepared without an automatic
commit:

```bash
git-crypt add-gpg-user -n USER_ID
```

The recipient needs the corresponding private GPG key and runs:

```bash
git-crypt unlock
```

Do not bypass GPG trust verification merely to make a failed grant succeed.

## Symmetric key

Export to a protected location outside the repository:

```bash
git-crypt export-key /secure/location/repository.key
git-crypt unlock /secure/location/repository.key
```

The first command is run by a current key holder; the second by the recipient
after secure delivery. Restrict the export's filesystem permissions and use
the agreed secure sharing channel. Never export to stdout or paste key
material into the conversation. Verify file existence and permissions without
reading it aloud.

If a repository key has leaked, treat the protected contents as exposed.
Rotate the application credentials and plan a new encryption setup; git-crypt
has no built-in key rotation or revocation workflow.

## Separate access groups

Named keys can protect different file sets:

```bash
git-crypt init -k frontend
git-crypt init -k backend
```

```gitattributes
frontend/config/.env filter=git-crypt-frontend diff=git-crypt-frontend
backend/secrets/** filter=git-crypt-backend diff=git-crypt-backend
```

Grant the relevant named key to each recipient, using `-n` if no commit is
wanted:

```bash
git-crypt add-gpg-user -n -k frontend FRONTEND_USER_ID
git-crypt add-gpg-user -n -k backend BACKEND_USER_ID
```

`git-crypt unlock` discovers the GPG-wrapped keys the recipient can decrypt.
Named keys restrict decryption, not filenames or repository write access.
Check that the intended files match the correct named filters before
committing.
