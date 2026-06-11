---
name: macos-input-method
description: >
  How to create macOS input methods (IME / Input Source) using Apple's InputMethodKit framework.
  Use this skill whenever the user wants to build a custom keyboard or input method for macOS,
  scaffold an InputMethodKit project, work with IMKInputController, set up an Input Source
  that appears in System Settings, or debug issues with InputMethodKit. Also trigger when
  the user mentions IMKServer, IMKCandidates, composing text / marked text in the context
  of macOS, bundle identifiers containing .inputmethod., Info.plist input method keys,
  or installing an app to ~/Library/Input Methods/.
---

# macOS Input Method Development

macOS input methods are built with Apple's **InputMethodKit** framework. An input method is a regular `.app` bundle (not an App Extension) that runs as a background process. The system manages its lifecycle automatically via `imklaunchagent`.

## Quick Start Checklist

1. Create a macOS Application target (type `APPL`)
2. Set Bundle Identifier to contain `.inputmethod.` (e.g., `com.example.inputmethod.MyIME`)
3. Add InputMethodKit-specific keys to Info.plist (see below)
4. Disable App Sandbox (`ENABLE_APP_SANDBOX = NO`)
5. Write `main.swift` - create `IMKServer` and run `NSApplication`
6. Write an `IMKInputController` subclass with `@objc(ClassName)` attribute
7. Build, copy to `~/Library/Input Methods/`, log out and back in

## Project Generation Workflow

When the user asks to create or scaffold a macOS input method, generate a
minimal working project rather than only explaining the API. Use XcodeGen by
default unless the repository already has an Xcode project convention.

Create or update these files:

- `project.yml` with a macOS application target, `ENABLE_APP_SANDBOX = NO`,
  manual signing for local development, and a bundle identifier containing
  `.inputmethod.`
- `Sources/main.swift` that creates a long-lived `IMKServer` and runs
  `NSApplication.shared.run()`
- `Sources/InputController.swift` with an `@objc(...)` `IMKInputController`
  subclass whose Objective-C name matches `InputMethodServerControllerClass`
- `Resources/ime_icon.tiff` or another real icon asset when the user provides
  one; otherwise leave the key out or call out that an icon still needs to be
  supplied
- `README.md` or setup notes with build, install, logout/login, and logging
  instructions when creating a new project

Before finishing a generated project, check these invariants:

- `PRODUCT_BUNDLE_IDENTIFIER` includes `.inputmethod.`
- `InputMethodConnectionName` matches the name passed to `IMKServer`
- `InputMethodServerControllerClass` matches the `@objc(...)` class name
- `LSBackgroundOnly` is `true`
- App Sandbox is disabled
- The install path is `~/Library/Input Methods/<AppName>.app`

## Project Structure

```
MyIME/
|-- project.yml               # XcodeGen config (run `xcodegen generate`)
|-- Info.plist
|-- Sources/
|   |-- main.swift            # Entry point: IMKServer + NSApplication.shared.run()
|   `-- InputController.swift # IMKInputController subclass
`-- Resources/
    `-- ime_icon.tiff         # Menu bar icon
```

Use XcodeGen (`xcodegen generate`) to produce the `.xcodeproj` from `project.yml`. This keeps the project file out of version control.

## Info.plist - Required Keys

Standard bundle keys plus these InputMethodKit-specific entries:

```xml
<key>LSBackgroundOnly</key>
<true/>

<key>InputMethodConnectionName</key>
<string>$(PRODUCT_BUNDLE_IDENTIFIER)_Connection</string>

<key>InputMethodServerControllerClass</key>
<string>MyInputController</string>

<key>tsInputMethodCharacterRepertoireKey</key>
<array>
    <string>Latn</string>
</array>

<key>tsInputMethodIconFileKey</key>
<string>ime_icon.tiff</string>
```

### Critical Rules

- **Bundle ID must contain `.inputmethod.`** - this is how macOS identifies the bundle as an input method. Without it, the app won't appear in Input Sources.
- **`InputMethodConnectionName`** must exactly match the `name` parameter passed to `IMKServer(name:bundleIdentifier:)`. The recommended pattern is `$(PRODUCT_BUNDLE_IDENTIFIER)_Connection`.
- **`InputMethodServerControllerClass`** must match the Objective-C class name set via `@objc(...)` on your `IMKInputController` subclass. No Swift module prefix needed.
- **`LSBackgroundOnly` must be `true`** - input methods are invisible background processes with no Dock icon.

### Character Repertoire Values

The `tsInputMethodCharacterRepertoireKey` determines which language category the input method appears under in System Settings:

| Value  | Category |
|--------|----------|
| `Latn` | English  |
| `Hans` | Simplified Chinese |
| `Hant` | Traditional Chinese |
| `Jpan` | Japanese |
| `Kore` | Korean |

Multiple values can be specified to appear in multiple categories.

## Entry Point (main.swift)

```swift
import Cocoa
import InputMethodKit

let connectionName = Bundle.main.infoDictionary?["InputMethodConnectionName"] as? String
    ?? "com.example.inputmethod.MyIME_Connection"

let server = IMKServer(name: connectionName, bundleIdentifier: Bundle.main.bundleIdentifier)
NSLog("MyIME: IMKServer started, connection=%@", connectionName)

NSApplication.shared.run()
```

Both `server` and `NSApplication.shared` must remain alive for the entire process lifetime. Using top-level variables in `main.swift` achieves this naturally.

Do not use `@main` together with `main.swift` - pick one approach. If you need an `AppDelegate` for more complex lifecycle management, read the reference file for the `NSApplication` subclass pattern.

## InputController

```swift
import Cocoa
import InputMethodKit

@objc(MyInputController)
class MyInputController: IMKInputController {

    override func inputText(_ string: String!, client sender: Any!) -> Bool {
        // Return false = passthrough (like ABC keyboard)
        // Return true  = event consumed (you handled it)
        return false
    }

    override func handle(_ event: NSEvent!, client sender: Any!) -> Bool {
        return false
    }
}
```

The `@objc(MyInputController)` attribute is required - InputMethodKit loads the class by name at runtime via the Objective-C runtime.

**Return value semantics**: `true` means "I handled this event, don't pass it to the app." `false` means "I didn't handle it, let the app receive it normally."

For composing text (marked text), candidate windows, and the full `IMKTextInput` client API, read `references/imkit-api.md`.

## XcodeGen Configuration (project.yml)

```yaml
name: MyIME

options:
  bundleIdPrefix: com.example
  deploymentTarget:
    macOS: "14.0"

settings:
  SWIFT_VERSION: "5"

targets:
  MyIME:
    type: application
    platform: macOS
    sources:
      - Sources
      - path: Resources
        buildPhase: resources
    info:
      path: Info.plist
      properties:
        CFBundleDisplayName: MyIME
        LSBackgroundOnly: true
        InputMethodConnectionName: $(PRODUCT_BUNDLE_IDENTIFIER)_Connection
        InputMethodServerControllerClass: MyInputController
        tsInputMethodCharacterRepertoireKey:
          - Latn
        tsInputMethodIconFileKey: ime_icon.tiff
    settings:
      PRODUCT_BUNDLE_IDENTIFIER: com.example.inputmethod.MyIME
      CODE_SIGN_IDENTITY: "-"
      CODE_SIGN_STYLE: Manual
      ENABLE_APP_SANDBOX: NO
```

The `info.properties` block injects InputMethodKit keys into the generated Info.plist. The `buildPhase: resources` on the Resources directory ensures files like the icon are copied into the app bundle.

## Installation

Install to `~/Library/Input Methods/` (per-user) or `/Library/Input Methods/` (system-wide, needs admin).

```bash
killall MyIME 2>/dev/null || true
sleep 0.5
rm -rf ~/Library/Input\ Methods/MyIME.app
cp -R /path/to/build/Debug/MyIME.app ~/Library/Input\ Methods/
```

- **First install**: requires logout + login (or restart) for macOS to discover the new Input Source.
- **Subsequent updates**: just `killall` + copy. The system relaunches the new version automatically when the input method is next activated.

After login, go to **System Settings > Keyboard > Input Sources**, click "Edit..." then "+", and find the input method under the appropriate language category.

## Debugging

- Use `NSLog()` - `print()` does not work because stdout is not connected for background agents.
- View logs in **Console.app**, filter by process name.
- Cannot press "Run" in Xcode to debug directly. Build, install to Input Methods, switch to the input method, and observe logs.

## Troubleshooting Decision Tree

Use this order when debugging. Most failures come from bundle metadata,
installation, or lifecycle issues rather than input handling code.

### Input method does not appear in System Settings

1. Confirm the built product is an `.app` bundle installed under
   `~/Library/Input Methods/` or `/Library/Input Methods/`.
2. Confirm the bundle identifier contains `.inputmethod.`.
3. Confirm `LSBackgroundOnly` is `true`.
4. Confirm `tsInputMethodCharacterRepertoireKey` contains the expected
   language category, such as `Latn`, `Hans`, or `Jpan`.
5. On first install, log out and back in or restart. Programmatic registration
   with `TISRegisterInputSource` can help install scripts, but do not assume it
   replaces all first-install discovery issues.

### `IMKServer` fails to register a connection

1. Disable App Sandbox with `ENABLE_APP_SANDBOX = NO`.
2. Verify `InputMethodConnectionName` exactly matches the name passed to
   `IMKServer(name:bundleIdentifier:)`.
3. Keep the `IMKServer` instance alive for the entire process lifetime. A local
   variable that goes out of scope can break the server.
4. Check Console.app logs from the input method process with `NSLog()`.

### Input controller is not loaded

1. Verify `InputMethodServerControllerClass` matches the `@objc(...)` name on
   the `IMKInputController` subclass.
2. Do not include a Swift module prefix in `InputMethodServerControllerClass`
   for the common `@objc(MyInputController)` pattern.
3. Confirm the source file is included in the app target.

### Keystrokes pass through unexpectedly

1. Remember that returning `false` means "not handled"; returning `true`
   consumes the input.
2. If both `handle(_:client:)` and `inputText(_:client:)` are implemented,
   `handle` can take precedence for key events.
3. Use `didCommandBySelector(_:client:)` for non-printable commands such as
   delete, arrows, enter, and escape when using text-level input handling.

### Candidate window is hidden or appears behind system UI

1. Treat `IMKCandidates` as a convenience API with known window-level issues on
   newer macOS releases.
2. For production-quality candidate UI, consider a custom `NSPanel` positioned
   from the `IMKTextInput` cursor rectangle. See `references/imkit-api.md`.

## App Sandbox

Input methods **must** disable App Sandbox, or `IMKServer` will fail with:
```
[IMKServer _createConnection]: *Failed* to register NSConnection
```

Set `ENABLE_APP_SANDBOX = NO` in build settings. Alternatively, add a temporary Mach service exception in entitlements - but disabling the sandbox entirely is simpler for development.

Input methods cannot be distributed via the Mac App Store.

## Further Reading

For detailed API documentation (composing text, candidate windows, IMKTextInput protocol, programmatic registration), see `references/imkit-api.md`.
