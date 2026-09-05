# Install or update an input source

Build the application and check the resulting bundle before replacing a
working installation. Use `~/Library/Input Methods/` for a per-user install;
use `/Library/Input Methods/` only for an intended system-wide install.

For a new per-user installation, substitute the actual built app path and
name:

```bash
mkdir -p "$HOME/Library/Input Methods"
ditto /path/to/build/Debug/MyIME.app "$HOME/Library/Input Methods/MyIME.app"
```

For an update, switch to another input source if necessary, stop only the
target input method process, and replace its installed bundle with the
complete build. Preserve a recoverable copy of the old bundle when replacement
could leave the user without a working input source. Avoid overlaying an old
bundle if obsolete resources would remain.

The system launches the installed version when the input source is activated.
On first installation, check System Settings > Keyboard > Input Sources and
add the source under its configured language category. If discovery has not
refreshed, a logout/login or restart may be necessary. Ask the user to perform
that step unless they have explicitly authorized a disruptive session action.

For requested automated registration, see the registration section of
[imkit-api.md](imkit-api.md). Registering, enabling, and selecting an input
source are distinct operations; registration alone does not guarantee UI
discovery.

Verify the installed bundle, its appearance in Input Sources, and the behavior
relevant to the task. If a login refresh or manual UI check remains, report it
as outstanding rather than claiming end-to-end verification.
