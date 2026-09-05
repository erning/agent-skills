# Create an InputMethodKit project

Generate a working minimal project when creation is requested. XcodeGen and
the layout below are defaults for a new project; preserve an existing Xcode
setup, entry point, deployment target, and directory layout when modifying
one.

Create the application target, server entry point, and input controller, then
check the shared invariants in [SKILL.md](../SKILL.md). Include build and
install notes for a new project. Build on macOS when available and fix
failures introduced by the change. If the environment cannot build it, report
that limitation.

## Project Structure

```
MyIME/
|-- project.yml               # XcodeGen config (run `xcodegen generate`)
|-- Info.plist
`-- Sources/
    |-- main.swift            # Entry point: IMKServer + NSApplication.shared.run()
    `-- InputController.swift # IMKInputController subclass
```

This example uses XcodeGen (`xcodegen generate`). Follow the target
repository’s existing project generation and version-control conventions when
they differ.

## Info.plist

In addition to standard bundle keys, use these InputMethodKit entries:

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
```

### Character Repertoire Values

The `tsInputMethodCharacterRepertoireKey` determines which language category
the input method appears under in System Settings:

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

Both `server` and `NSApplication.shared` must remain alive for the entire
process lifetime. Using top-level variables in `main.swift` achieves this
naturally.

Do not use `@main` together with `main.swift` - pick one approach. If you need
an `AppDelegate` for more complex lifecycle management, read
[imkit-api.md](imkit-api.md) for the `NSApplication` subclass pattern.

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
}
```

The `@objc(MyInputController)` attribute is required - InputMethodKit loads
the class by name at runtime via the Objective-C runtime.

**Return value semantics**: `true` means "I handled this event, don't pass it
to the app." `false` means "I didn't handle it, let the app receive it
normally."

For marked text and candidates, read [imkit-api.md](imkit-api.md).

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
    info:
      path: Info.plist
      properties:
        CFBundleDisplayName: MyIME
        LSBackgroundOnly: true
        InputMethodConnectionName: $(PRODUCT_BUNDLE_IDENTIFIER)_Connection
        InputMethodServerControllerClass: MyInputController
        tsInputMethodCharacterRepertoireKey:
          - Latn
    settings:
      PRODUCT_BUNDLE_IDENTIFIER: com.example.inputmethod.MyIME
      CODE_SIGN_IDENTITY: "-"
      CODE_SIGN_STYLE: Manual
      ENABLE_APP_SANDBOX: NO
```

The `info.properties` block injects the keys into the generated Info.plist. If
an icon is available, add its real file to the resources build phase and set
`tsInputMethodIconFileKey` to its bundled name. Omit the key when no asset
exists.
