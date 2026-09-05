# Diagnose InputMethodKit problems

Start with the observed symptom and the available logs. These are likely
causes and useful checks, not a required order for every failure.

## Input method does not appear in System Settings

1. Confirm the built product is an `.app` bundle installed under
   `~/Library/Input Methods/` or `/Library/Input Methods/`.
2. Confirm the bundle identifier contains `.inputmethod.`.
3. Confirm `LSBackgroundOnly` is `true`.
4. Confirm `tsInputMethodCharacterRepertoireKey` contains the expected
   language category, such as `Latn`, `Hans`, or `Jpan`.
5. If discovery still fails after first installation, a logout/login or
   restart may be needed. Programmatic registration with
   `TISRegisterInputSource` can help install scripts, but does not resolve
   every discovery problem.

## `IMKServer` fails to register a connection

1. Disable App Sandbox with `ENABLE_APP_SANDBOX = NO`.
2. Verify `InputMethodConnectionName` exactly matches the name passed to
   `IMKServer(name:bundleIdentifier:)`.
3. Keep the `IMKServer` instance alive for the entire process lifetime. A
   local variable that goes out of scope can break the server.
4. Check Console.app logs from the input method process with `NSLog()`.

## Input controller is not loaded

1. Verify `InputMethodServerControllerClass` matches the `@objc(...)` name on
   the `IMKInputController` subclass.
2. Do not include a Swift module prefix in `InputMethodServerControllerClass`
   for the common `@objc(MyInputController)` pattern.
3. Confirm the source file is included in the app target.

## Keystrokes pass through unexpectedly

1. Remember that returning `false` means "not handled"; returning `true`
   consumes the input.
2. If both `handle(_:client:)` and `inputText(_:client:)` are implemented,
   `handle` can take precedence for key events.
3. Use `didCommand(by:client:)` for non-printable commands such as delete,
   arrows, enter, and escape when using text-level input handling.

## Candidate window is hidden or appears behind system UI

1. Treat `IMKCandidates` as a convenience API with known window-level issues
   on newer macOS releases.
2. For production-quality candidate UI, consider a custom `NSPanel` positioned
   from the `IMKTextInput` cursor rectangle. See [imkit-api.md](imkit-api.md).

## Process logs

Use `NSLog()` or the repository's existing unified logging approach. Inspect
logs in Console.app by process name; stdout from `print()` may not be visible
for a system-launched input method. Reproduce problems through the installed
input source. Running the app directly in Xcode does not reproduce that entire
path.
