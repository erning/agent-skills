# InputMethodKit API Reference

## Table of Contents

1. [Core Classes](#core-classes)
2. [Entry Point Patterns](#entry-point-patterns)
3. [Input Handling Approaches](#input-handling-approaches)
4. [IMKTextInput Client Protocol](#imktextinput-client-protocol)
5. [Composing Text (Marked Text)](#composing-text-marked-text)
6. [Candidate Windows](#candidate-windows)
7. [Menus And Preferences](#menus-and-preferences)
8. [Lifecycle Methods](#lifecycle-methods)
9. [Programmatic Registration](#programmatic-registration)
10. [Known Issues](#known-issues)
11. [Official References](#official-references)
12. [Reference Projects](#reference-projects)

---

## Core Classes

| Class | Role |
|-------|------|
| `IMKServer` | Main server. Registers a Mach service so macOS can route input events to the process. One per app, must stay alive forever. |
| `IMKInputController` | Subclass this to handle input. The system creates one instance per active text input session (one per focused text field). |
| `IMKCandidates` | Optional. Manages a candidate/suggestion window. Has known bugs on macOS 10.14+. |

---

## Entry Point Patterns

### Pattern A: main.swift (simple)

```swift
import Cocoa
import InputMethodKit

let connectionName = Bundle.main.infoDictionary?["InputMethodConnectionName"] as? String
    ?? "com.example.inputmethod.MyIME_Connection"

let server = IMKServer(name: connectionName, bundleIdentifier: Bundle.main.bundleIdentifier)
NSLog("MyIME: IMKServer started")

NSApplication.shared.run()
```

Cannot coexist with `@main`. Top-level variables live for the process lifetime, which is what IMKServer needs.

### Pattern B: NSApplication subclass + @main (complex lifecycle)

```swift
import Cocoa
import InputMethodKit

class IMEApplication: NSApplication {
    private let appDelegate = AppDelegate()
    override init() {
        super.init()
        self.delegate = appDelegate
    }
    required init?(coder: NSCoder) { fatalError() }
}

@main
class AppDelegate: NSObject, NSApplicationDelegate {
    var server: IMKServer!
    var candidates: IMKCandidates!

    func applicationDidFinishLaunching(_ notification: Notification) {
        let name = Bundle.main.infoDictionary?["InputMethodConnectionName"] as? String
        server = IMKServer(name: name, bundleIdentifier: Bundle.main.bundleIdentifier)
        candidates = IMKCandidates(
            server: server,
            panelType: kIMKSingleColumnScrollingCandidatePanel,
            styleType: kIMKMain
        )
    }
}
```

When using this pattern, add to Info.plist:
```xml
<key>NSPrincipalClass</key>
<string>$(PRODUCT_MODULE_NAME).IMEApplication</string>
```

---

## Input Handling Approaches

IMKInputController supports three mutually exclusive input handling approaches. Choose one:

### Approach 1: Text-level (recommended for simple input methods)

```swift
// Called when a printable character is typed
override func inputText(_ string: String!, client sender: Any!) -> Bool {
    // string: the character produced by the keystroke (e.g., "a", "B", "1")
    // return true if handled, false to passthrough
    return false
}

// Called for non-printable keys (arrows, delete, escape, etc.)
override func didCommandBySelector(_ aSelector: Selector!, client sender: Any!) -> Bool {
    // aSelector: e.g., #selector(deleteBackward:), #selector(moveLeft:)
    return false
}
```

### Approach 2: Key + modifiers

```swift
override func inputText(_ string: String!, key keyCode: Int,
                         modifiers flags: Int, client sender: Any!) -> Bool {
    // keyCode: hardware key code
    // flags: modifier flags (shift, command, option, control)
    return false
}
```

### Approach 3: Raw NSEvent (full control)

```swift
override func handle(_ event: NSEvent!, client sender: Any!) -> Bool {
    guard let event = event else { return false }

    switch event.type {
    case .keyDown:
        let keyCode = event.keyCode
        let modifiers = event.modifierFlags
        let characters = event.characters ?? ""
        // handle the key event
        return false
    case .flagsChanged:
        // modifier key pressed/released
        return false
    default:
        return false
    }
}
```

If both `inputText` and `handle` are implemented, `handle` takes precedence for key events.

---

## IMKTextInput Client Protocol

The `sender` / `client` parameter conforms to `IMKTextInput`. Cast it to access text interaction methods:

```swift
guard let client = sender as? (any IMKTextInput) else { return false }
```

### Key Methods

```swift
// Insert finalized text at the cursor (or replace the marked text region)
client.insertText(
    "text to insert",
    replacementRange: NSRange(location: NSNotFound, length: NSNotFound)
)

// Set composing / marked text (pre-edit text shown with underline)
client.setMarkedText(
    "composing text",
    selectionRange: NSRange(location: 5, length: 0),       // cursor within marked text
    replacementRange: NSRange(location: NSNotFound, length: NSNotFound)
)

// Get the current selection range
let selection: NSRange = client.selectedRange()

// Get text in a specific range
let text: String? = client.string(from: someRange) as? String

// Get cursor screen position (for positioning candidate window)
var lineHeightRect = NSRect.zero
client.attributes(forCharacterIndex: 0, lineHeightRectangle: &lineHeightRect)
// lineHeightRect now contains the cursor's screen coordinates
```

### NSRange Convention

When a range is not applicable, use `NSRange(location: NSNotFound, length: NSNotFound)`. This tells the system to use the default behavior (e.g., insert at cursor, replace current marked text).

---

## Composing Text (Marked Text)

Chinese, Japanese, and other input methods show "work-in-progress" text before the user confirms a candidate. This is called marked text (or composing text) - it typically renders with an underline.

### Workflow

```
User types "zhong" -> show marked text "zhong" -> user selects "zhong1" -> insert "example"
```

```swift
var composingBuffer = ""

override func inputText(_ string: String!, client sender: Any!) -> Bool {
    guard let client = sender as? (any IMKTextInput) else { return false }

    composingBuffer += string

    // Show composing buffer as marked text
    client.setMarkedText(
        composingBuffer,
        selectionRange: NSRange(location: composingBuffer.count, length: 0),
        replacementRange: NSRange(location: NSNotFound, length: NSNotFound)
    )

    // Update candidate window
    // ...

    return true
}

// When user confirms (e.g., presses Enter or selects a candidate)
func commitText(_ text: String, client: any IMKTextInput) {
    client.insertText(
        text,
        replacementRange: NSRange(location: NSNotFound, length: NSNotFound)
    )
    composingBuffer = ""
}
```

### Styled Marked Text

Use `NSAttributedString` for more control over marked text appearance:

```swift
let attributed = NSAttributedString(
    string: composingBuffer,
    attributes: [
        .underlineStyle: NSUnderlineStyle.single.rawValue,
        .foregroundColor: NSColor.textColor
    ]
)
client.setMarkedText(
    attributed,
    selectionRange: NSRange(location: composingBuffer.count, length: 0),
    replacementRange: NSRange(location: NSNotFound, length: NSNotFound)
)
```

---

## Candidate Windows

### Using IMKCandidates (built-in)

```swift
// Create in AppDelegate or main.swift alongside IMKServer
let candidates = IMKCandidates(
    server: server,
    panelType: kIMKSingleColumnScrollingCandidatePanel,
    styleType: kIMKMain
)
```

Panel types:
- `kIMKSingleColumnScrollingCandidatePanel` - vertical scrolling list
- `kIMKSingleRowSteppingCandidatePanel` - horizontal row, step through with arrows
- `kIMKScrollingGridCandidatePanel` - grid layout

### Providing Candidates

Override in your `IMKInputController` subclass:

```swift
override func candidates(_ sender: Any!) -> [Any]! {
    return ["candidate1", "candidate2", "candidate3"]
}
```

### Handling Selection

```swift
override func candidateSelected(_ candidateString: NSAttributedString!) {
    guard let client = self.client() as? (any IMKTextInput) else { return }
    client.insertText(
        candidateString.string,
        replacementRange: NSRange(location: NSNotFound, length: NSNotFound)
    )
}

override func candidateSelectionChanged(_ candidateString: NSAttributedString!) {
    // Preview the selected candidate (optional)
}
```

### Show / Hide

```swift
// Show candidates (typically after composing buffer changes)
candidates.update()
candidates.show()

// Hide candidates (after committing text or clearing buffer)
candidates.hide()
```

### Custom Candidate Window

Many production input methods skip `IMKCandidates` and implement their own window using `NSPanel` because of known bugs (see Known Issues). The general approach:

1. Create an `NSPanel` with `level = .popUpMenu` and `styleMask = [.borderless, .nonactivatingPanel]`
2. Position it near the cursor using `client.attributes(forCharacterIndex:lineHeightRectangle:)`
3. Populate with your own UI (SwiftUI or AppKit)
4. Handle arrow key / number key selection in your `InputController`

---

## Menus And Preferences

InputMethodKit does not provide a full preferences UI framework. It provides entry points that let the input method expose commands, define input modes, and open its own settings UI.

### Relevant APIs

- `IMKInputController.menu()`
- `IMKInputController.doCommand(by:command:)`
- `IMKStateSetting.showPreferences(_:)`
- `IMKStateSetting.modes(_:)`

### Menu Versus Modes

These APIs solve different problems:

- `menu()` defines command items shown in the input method menu
- `modes(_:)` defines the formal input modes exposed by the input method

Use `menu()` for actions such as:

- `Preferences...`
- reload config
- open dictionary tools
- toggle temporary options

Use `modes(_:)` for durable system-level modes such as:

- phonetic mode versus direct ASCII mode
- hiragana versus katakana versus roman
- full-width versus half-width

In short:

- `menu()` answers "what commands can the user invoke?"
- `modes(_:)` answers "what input modes does this input method support?"

### Practical Model

1. Return an input method menu from `menu()`
2. Add a `Preferences...` item to that menu
3. Route the command through `doCommand(by:command:)` or an action method
4. Open a normal AppKit preferences window from `showPreferences(_:)`
5. Return the mode dictionary from `modes(_:)` when the input method has multiple formal modes
6. Store settings in `UserDefaults` or a shared defaults suite

### Design Notes

- The settings window is typically a normal `NSWindowController` plus `NSViewController`
- `showPreferences(_:)` is only the entry point, not the UI implementation
- If the project uses a separate settings app, the input method menu can launch that app instead of hosting the full UI itself
- `modes(_:)` is for system-facing mode definitions, not for every internal state flag
- In practice, mode definitions usually correspond to `ComponentInputModeDict` in `Info.plist`

---

## Lifecycle Methods

```swift
// Called when user switches TO this input method
override func activateServer(_ sender: Any!) {
    super.activateServer(sender)
    // Initialize state, load preferences, etc.
}

// Called when user switches AWAY from this input method
override func deactivateServer(_ sender: Any!) {
    super.deactivateServer(sender)
    // Clean up, commit any pending text
}

// Return recognized event types (default: key events)
override func recognizedEvents(_ sender: Any!) -> Int {
    let start = NSEvent.EventTypeMask.keyDown
    return Int(start.rawValue)
}

// Open preferences window
override func showPreferences(_ sender: Any!) {
    // Show a preferences window or panel
}

// Return supported input modes (for input methods with multiple modes)
override func modes(_ sender: Any!) -> [AnyHashable : Any]! {
    return nil  // single-mode input method
}
```

### What `modes(_:)` Represents

`modes(_:)` returns the input method mode dictionary. The public documentation is sparse, but older InputMethodKit references and bundle metadata indicate that this dictionary describes:

- which input modes exist
- which modes are visible
- the order of visible modes
- per-mode metadata such as icons and default state

At a high level, it is commonly modeled like this:

```text
mode dictionary
- tsInputModeListKey
  - mode id -> mode properties
- tsVisibleInputModeOrderedArrayKey
  - ordered list of visible mode ids
```

Typical per-mode properties may include:

- mode identifier
- menu icon
- alternate icon
- visibility
- default state
- key equivalent

If the input method only has one mode, this can stay minimal. If the input method has several durable modes, the mode IDs and their ordering matter.

---

## Programmatic Registration

Register an input method without requiring logout - useful in install scripts:

```swift
import Carbon

let path = "\(NSHomeDirectory())/Library/Input Methods/MyIME.app"
let url = URL(fileURLWithPath: path)

// Register the bundle with the system
TISRegisterInputSource(url as CFURL)

// Find the input source by bundle ID
let conditions = NSMutableDictionary()
conditions.setValue("com.example.inputmethod.MyIME",
                    forKey: kTISPropertyBundleID as String)

if let sources = TISCreateInputSourceList(conditions, true)?
    .takeRetainedValue() as? [TISInputSource],
   let source = sources.first {
    TISEnableInputSource(source)     // make it available in Input Sources list
    TISSelectInputSource(source)     // switch to it immediately (optional)
}
```

This uses the Carbon `Text Input Source Services` API. Import `Carbon` to access these functions.

---

## Known Issues

- **IMKCandidates window level**: On macOS 10.14+, the built-in candidate window gets obscured by NSMenu, Spotlight, and other system UI. Workaround: use `setWindowLevel:` (private API) or implement a custom candidate window.

- **Sandbox incompatibility**: `IMKServer` requires registering a global Mach service, which App Sandbox blocks. Either disable sandbox or add a `com.apple.security.temporary-exception.mach-register.global-name` entitlement.

- **No App Store distribution**: Apple does not allow InputMethodKit apps on the Mac App Store.

- **Xcode debugging limitations**: Input methods must be installed to `~/Library/Input Methods/` and launched by the system. You cannot run them directly from Xcode. Use `NSLog` + Console.app for debugging.

- **First-install discovery**: macOS discovers new input sources at login time. The very first install requires a logout/login cycle. Subsequent updates only need a process restart.

- **`print()` does not work**: stdout is not connected for background processes launched by `imklaunchagent`. Always use `NSLog()`.

---

## Official References

- InputMethodKit framework:
  https://developer.apple.com/documentation/inputmethodkit
- `IMKServer.init(name:bundleIdentifier:)`:
  https://developer.apple.com/documentation/inputmethodkit/imkserver/init%28name%3Abundleidentifier%3A%29
- `IMKInputController`:
  https://developer.apple.com/documentation/inputmethodkit/imkinputcontroller
- `IMKCandidates`:
  https://developer.apple.com/documentation/inputmethodkit/imkcandidates
- `IMKStateSetting`:
  https://developer.apple.com/documentation/inputmethodkit/imkstatesetting
- `showPreferences(_:)`:
  https://developer.apple.com/documentation/inputmethodkit/imkstatesetting/showpreferences%28_%3A%29
- `modes(_:)`:
  https://developer.apple.com/documentation/inputmethodkit/imkstatesetting/modes%28_%3A%29
- `menu()`:
  https://developer.apple.com/documentation/inputmethodkit/imkinputcontroller/menu%28%29
- `doCommand(by:command:)`:
  https://developer.apple.com/documentation/inputmethodkit/imkinputcontroller/1385553-docommand
- `NSTextInputClient`:
  https://developer.apple.com/documentation/appkit/nstextinputclient
- Apple QA1810:
  https://developer.apple.com/library/archive/qa/qa1810/_index.html

---

## Reference Projects

- [ensan-hcl/macOS_IMKitSample_2021](https://github.com/ensan-hcl/macOS_IMKitSample_2021) - Swift, modern, most complete example
- [pkamb/NumberInput_IMKit_Sample](https://github.com/pkamb/NumberInput_IMKit_Sample) - Apple's official sample (Objective-C)
- [pkamb/InputMethodKitBoilerplate](https://github.com/pkamb/InputMethodKitBoilerplate) - Minimal Objective-C boilerplate
- [google/mozc](https://github.com/google/mozc) - Production input method (Google Japanese Input)
