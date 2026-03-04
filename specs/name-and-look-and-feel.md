This project name is `RW Notes`, so any user facing mention of SiYuan shall be changed to `RW Notes` or `rw-notes`.

This includes packaging labels, runtime window titles, manifests, translation strings, and bundled end-user content such as guides. Previous changelogs shall remain untouched, as they are historical references.

Internal compatibility identifiers may temporarily keep upstream naming when changing them would break packaging, upgrade paths, protocol handling, user data locations, or OS integration. Examples include protocol schemes, user agent tokens, kernel binary names, and AppX identity names. Those cases shall be treated as explicit compatibility exceptions and migrated only in a dedicated compatibility pass.

The current package/application identifiers for the fork shall be:

- Electron builder `appId`: `com.parendum.rwnotes`
- Web manifest application id: `com.parendum.rwnotes`
- Windows AppX package identity name: `com.parendum.rwnotes`

The icon for all purposes shall be the one defined at `app/src/assets/icon.svg`, and the rest of the icon assets are derived from that source file.

The project slogan shall be `Your better brain` in current end-user copy and packaging metadata. Historical changelogs and file headers shall remain untouched.

The repository shall maintain a single top-level `README.md` in English. Translated top-level README variants are not maintained in this fork.

Derived icon assets shall not be edited manually. They must be regenerated from `app/src/assets/icon.svg` through `app/src/assets/generate_icons.py`.

The generated asset set currently includes:

- `app/src/assets/icon.png`
- `app/src/assets/icon256.png`
- `app/src/assets/icon-mac.png`
- `app/src/assets/icon.ico`
- `app/src/assets/icon.icns`
- `app/stage/icon.png`
- `app/stage/icon-large.png`
- `app/appearance/boot/icon.png`
- `app/electron/icon.png`
- `kernel/resource/icon.ico`
- all PNG assets under `app/appx/assets/`

When the source icon changes, the generator script shall be run so desktop packaging, boot screens, tray icons, and Windows Store/AppX assets stay aligned.
