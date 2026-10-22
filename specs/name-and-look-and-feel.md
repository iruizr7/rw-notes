# Name, Product Language, and Look and Feel

This project name is `RW Notes`. User-facing product branding shall use `RW Notes` or `rw-notes`. Factual references to upstream SiYuan, source attribution, copyright/license notices, and historical context shall remain accurate; they are not branding replacement targets.

This includes packaging labels, runtime window titles, manifests, translation strings, and bundled end-user content such as guides. Previous changelogs shall remain untouched, as they are historical references.

Internal compatibility identifiers should keep upstream naming when changing them would break packaging, upgrade paths, protocol handling, user data locations, or OS integration. Examples include protocol schemes, user agent tokens, kernel binary names, and AppX identity names. Those cases shall be treated as explicit compatibility exceptions. There is no requirement to rename them merely to complete branding; any future migration needs a dedicated compatibility plan and a concrete benefit. The global objective is low to medium effort when merging upstream changes.

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

## Product Language for v0

The product vision and release scope are defined in [saas-plan.md](./saas-plan.md). UI and documentation must distinguish planned features from capabilities already delivered.

- **Upstream** means the official SiYuan repository. Use this term consistently in development documentation.
- **Organization** is the membership boundary; **workspace** is its shared knowledge base. In v0 these are one-to-one. Do not present multiple workspaces inside an org as an available feature.
- Remove inherited SiYuan cloud, Liuyun, and Liandi account, subscription/payment, cloud-region, storage/quota, sync, and publishing surfaces, along with promotional and setup copy for those services. RW Notes identity and sync UI must be independent of upstream vendor accounts. Preserve factual attribution, historical records, and user-authored links.
- Role labels are exactly **Admin**, **Write**, and **Read**, applying to the whole workspace. Internal upstream constants may retain administrator/editor/reader terminology.
- AI agents are identifiable participants. Show the actor responsible for a change and the delegating user where applicable.
- Desktop and mobile support offline-first editing in the v0 target. Distinguish **Saved locally**, **Syncing**, **Synced**, and **Could not sync**; do not imply a local save has already reached other devices.
- Conflicts resolve automatically by timestamp. Show an understandable notice and access to the displaced version in history; avoid implying that both edits were merged into the winning text.
- Near-realtime describes connected updates. Show offline/reconnecting state honestly; mobile suspension requires catch-up on resume.
- v1 email/push notifications, summaries, and Todoist-like database task management remain future candidates and must not be advertised as delivered v0 features.

## UI Preservation

Reuse the upstream editor and shared web, desktop, and mobile UI. Add only the surfaces needed for organization/membership management, role-aware actions, personal settings, sync status, and recoverable history. A new service identity does not require an editor or application-shell redesign.

Keep common labels and interaction behavior consistent across clients while respecting platform-specific controls. New English user-facing copy follows the repository's primary language policy; preserve upstream translation keys and shared UI structures where practical to reduce merge effort.
