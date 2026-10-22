# Project Architecture

This document describes how RW Notes is put together so future agents can find the correct layer before changing behavior.

It is intentionally practical rather than exhaustive. The runtime/package sections provide a navigation map, originally reviewed on 3.5.8 and pending a full M0 refresh against 3.8.8; the final target-architecture section describes planned work, not implemented capabilities. When the architecture changes materially, this file should be updated in the same change.

Product scope, terms, roles, reconciliation rules, and delivery gates are defined in [saas-plan.md](./saas-plan.md). That plan is authoritative for the v0 target.

## Fork Context

- **Upstream** means the official SiYuan repository, `siyuan-note/siyuan`. This repository is the RW Notes fork and still keeps many internal compatibility identifiers as `siyuan`.
- As described in `AGENTS.md`, `master` tracks upstream and `rw-notes` is the project development branch, receiving periodic merges from `master`. Branch policy does not imply a Git remote named `upstream` is already configured.
- Preserve upstream storage, editor, and shared UI as primary compatibility surfaces. Also preserve stable IDs/references, attribute-view formats, content APIs where feasible, history/import/export, and native/build contracts. See the compatibility objectives in the SaaS plan.
- User-facing naming should follow [name-and-look-and-feel.md](./name-and-look-and-feel.md).
- Internal names such as protocol handlers, config paths, environment variables, Go module paths, Electron IPC channel names, and some runtime globals may still use upstream naming. Do not mass-rename those unless explicitly told to.

## Top-Level Shape

### Related mobile forks

Native apps are maintained as separate GitHub forks, checked out beside this repository under the workspace's `repos/` directory:

| Platform | Fork | Sibling checkout |
| --- | --- | --- |
| Android | [iruizr7/rw-notes-android](https://github.com/iruizr7/rw-notes-android) | `../rw-notes-android/` |
| iOS | [iruizr7/rw-notes-ios](https://github.com/iruizr7/rw-notes-ios) | `../rw-notes-ios/` |

Each mobile checkout uses `origin` for our fork and `upstream` for the corresponding official `siyuan-note/siyuan-*` repository. Its clean `main` branch tracks `upstream/main`; `rw-notes` tracks `origin/rw-notes` and is the fork's default development branch. Fetch upstream changes into the tracking branch first, then deliberately select an integration revision for `rw-notes`; do not automatically import the latest mobile head. Preserve the core repository's existing `master`/`rw-notes` structure.

The selected source baseline is now core/Android **3.8.8** and iOS **`05280f32ba89705e3ba55c233037db02c93cdea8`**. [upstream-baseline.md](./upstream-baseline.md) records full SHAs, integration decisions and validation status. Native compatibility still needs matching frontend/kernel builds and device checks; the selected iOS SHA is not proven to be the App Store build source. Mobile development targets Android and iOS; HarmonyOS is out of scope.

### Core repository directories

- `app/`: TypeScript frontend, Electron desktop shell, static assets, themes, icons, bundled guide content, and webpack build definitions.
- `kernel/`: Go backend process responsible for workspace boot, HTTP/WebSocket serving, persistence, indexing, sync, import/export, and most business logic.
- `specs/`: Fork-specific project decisions and architectural notes. New cross-cutting behavior should usually be reflected here.
- `scripts/`: Release/build helpers and maintenance scripts.

In normal desktop operation there are two cooperating processes:

- Electron UI process from `app/electron/main.js`.
- Go kernel process from `kernel/main.go`.

In browser or Docker-style deployments, the Go kernel can serve the frontend assets directly without Electron.

## Runtime Model

### 1. Boot

- `kernel/main.go` is the non-mobile kernel entrypoint; `kernel/mobile/kernel.go` exposes the mobile kernel integration.
- `kernel/util/working.go` parses CLI flags and environment variables, resolves the workspace, prepares paths, enforces the workspace lock, and sets runtime globals.
- `kernel/model/conf.go` loads and normalizes persisted app configuration.
- `kernel/sql/*.go` initializes SQLite databases and search indexes.
- `kernel/server/serve.go` starts the Gin HTTP server, static asset routes, `/ws`, DAV services, and `/api/*`.
- Background services then start from `kernel/job`, `kernel/cache`, asset watchers, emoji watchers, sync bootstrapping, and filesystem health checks.

### 2. UI startup

- `app/src/index.ts` is the main frontend entrypoint for the app UI.
- The frontend first requests `/api/system/getConf`.
- It then loads language assets from `/appearance/langs/*.json`, initializes layout and menus, and opens a WebSocket to `/ws`.
- Most live refresh behavior is driven by kernel-pushed WebSocket messages handled through `app/src/layout/Model.ts`.

### 3. Desktop shell

- `app/electron/main.js` is the desktop orchestrator.
- It owns native window management, tray behavior, protocol handling, desktop IPC, and spawning/monitoring the Go kernel.
- Electron talks to the kernel over local HTTP like any other client. It is not the source of business logic.

## Layer Ownership

The most important architectural rule is:

- `app/` owns presentation, client-side interaction, and Electron integration.
- `kernel/api/` owns HTTP route binding and request/response shaping.
- `kernel/model/` owns business logic and workflow orchestration.
- `kernel/sql/` owns SQLite persistence and indexing queries.
- `kernel/util/` owns runtime environment, filesystem helpers, OS integration, shared helpers, and bootstrapping primitives.

In most features the call path is:

- frontend action
- `fetchPost("/api/...")` or WebSocket command from `app/src`
- handler in `kernel/api`
- business logic in `kernel/model`
- persistence/index/filesystem work in `kernel/sql`, `kernel/filesys`, `kernel/treenode`, `kernel/cache`, or `kernel/util`
- optional live update event back to clients via WebSocket (distinct from the planned v1 email/mobile push notifications)

If a change requires modifying both `kernel/api` and `kernel/model`, the API file should stay thin. Push real logic down into `model`.

## Important Backend Packages

- `kernel/api/`: Public HTTP API surface. Files are grouped by feature area such as `block`, `filetree`, `history`, `repo`, `sync`, `setting`, and `system`.
- `kernel/model/`: Core application behavior. This is the first place to look for notebook, document, sync, export, AI, bazaar, rendering, watcher, and transaction behavior.
- `kernel/sql/`: SQLite schema, FTS, history DB, asset content DB, queue handling, and index queries.
- `kernel/treenode/`: In-memory and persisted block tree structures used by document/block operations.
- `kernel/filesys/`: Filesystem-backed tree and template support.
- `kernel/conf/`: Typed config structures used by `model.Conf`.
- `kernel/server/`: HTTP server assembly, auth/session middleware, static serving, WebSocket, proxy, and DAV endpoints.
- `kernel/task/` and `kernel/job/`: Queues and scheduled work.
- `kernel/bazaar/`: Marketplace package handling for widgets, plugins, icons, themes, and templates.
- `kernel/av/`: Attribute-view and database-style layout logic.

## Important Frontend Areas

- `app/src/index.ts`: Main app bootstrap.
- `app/src/window/`: Secondary window bootstrap and behavior.
- `app/src/layout/`: Layout tree, tabs, windows, docks, and WebSocket-backed models.
- `app/src/editor/` and `app/src/protyle/`: Editing experience and Protyle integration.
- `app/src/config/`: Settings UI and related client-side helpers.
- `app/src/plugin/`: Frontend plugin API and plugin loading.
- `app/src/mobile/`: Mobile-specific UI entrypoint and behavior.
- `app/src/assets/`: SCSS, templates, icons, and generated assets.
- `app/electron/`: Desktop-only shell behavior.
- `app/appearance/`: Themes, icon sets, fonts, boot assets, and translations served by the kernel.

## Build Outputs

- `app/package.json` defines the frontend and packaging tasks.
- `app/webpack.config.js` builds the Electron-renderer app pages into `app/stage/build/app`.
- `app/webpack.desktop.js` builds the browser/desktop target into `app/stage/build/desktop`.
- `app/webpack.mobile.js` builds the mobile web target into `app/stage/build/mobile`.
- `app/webpack.export.js` builds export-related assets.
- `Dockerfile` builds frontend assets first, then builds the Go kernel, then assembles a final Alpine runtime image.

The static assets copied into production are not just compiled JS/CSS. They also include:

- `appearance/`
- `stage/`
- `guide/`
- `changelogs/`

## Workspace Layout

The kernel treats the workspace as the main mutable state root. `kernel/util/working.go` sets these paths:

- `conf/`: persisted app configuration for the workspace.
- `data/`: notebooks, assets, templates, plugins, widgets, emojis, snippets, and public files.
- `repo/`: snapshot/repository data.
- `history/`: historical data outside the main DB.
- `temp/`: runtime databases, logs, and temporary files.

Important details:

- The main SQLite databases live under `workspace/temp/`, not at repository root.
- The kernel also keeps compatibility state under `~/.config/siyuan/`, including `workspace.json`, `port.json`, shortcuts, and some desktop boot metadata.
- The workspace is single-writer guarded by a lock file. Planned offline devices need distinct local replicas; independent kernels must not share one writable workspace volume.
- Core SQLite indexes can be rebuilt from content. Planned identity, pending operations, conflict history, and synchronization metadata require separate durable storage and must not depend on index rebuilds preserving them.

## Communication Patterns

### HTTP API

- Most client mutations and reads go through `POST /api/...`.
- `kernel/api/router.go` is the main registration point.
- Authentication, role checks, and read-only checks are applied in the API layer before reaching business logic. Current shared access-code/API-token paths grant administrator access; many content and preference routes also require administrator privileges. This is not yet the v0 membership model.
- Existing `RoleAdministrator`, `RoleEditor`, and `RoleReader` constants can map to product roles **Admin**, **Write**, and **Read**. Every route still needs classification by capability; simply assigning these constants does not implement the intended permissions.

### WebSocket

- `/ws` is used for live UI updates, reloads, progress, sync notifications, and some command-style messages.
- `app/src/layout/Model.ts` is the main client-side abstraction for WebSocket connections.
- Kernel pushes are important for keeping multiple windows/sessions coherent. If a backend change mutates visible state, check whether a push/reload message is also needed.
- Existing broadcasts are not a durable replay or offline reconciliation protocol. v0 needs actor/workspace identity, ordered event cursors, reconnect recovery, and safe application while a client has local pending edits. Do not treat a reload as sufficient concurrent-edit handling.

### Static Serving

- The kernel serves built frontend files, appearance assets, snippets, templates, plugins, widgets, guide content, exports, and public assets.
- Desktop Electron windows still load from the kernel HTTP server, not from local files for the main app surface.

## Typical Change Routing

Use this as the default decision guide:

- UI layout, dialogs, menus, editor interactions, client-side validation: start in `app/src`.
- New API endpoint or changing request/response shape: `kernel/api`.
- Notebook, block, sync, search, export, AI, history, or repo behavior: `kernel/model`.
- Query correctness, indexing, FTS, or persistence schema: `kernel/sql`.
- Workspace pathing, boot flags, env vars, filesystem helpers, OS integration: `kernel/util`.
- Desktop-only behavior such as windows, tray, native dialogs, protocol registration: `app/electron`.
- Theme, language, icon, boot asset, or packaging identity changes: `app/appearance`, `app/src/assets`, packaging configs, and the related spec files.

## Architectural Constraints And Pitfalls

- Many runtime identifiers intentionally still use `siyuan`; changing them can break upgrade paths, protocol handling, config discovery, and interoperability.
- The frontend global is still `window.siyuan` in many places. Treat that as compatibility state, not a rename target by default.
- The kernel serializes many API requests intentionally through middleware. Be careful with concurrency assumptions.
- A lot of behavior depends on both filesystem state and SQLite indexes. If content changes but search/backlinks/history look stale, inspect both model logic and SQL/index refresh paths.
- Desktop, browser, Docker, and mobile targets share a large amount of code but not all boot paths. Verify target-specific entrypoints before changing boot or asset assumptions.
- Existing upstream comments and issue references are often the best explanation for why a behavior looks unusual. Do not delete them casually.

## Expectations For Future Specs

This file should be updated when any of the following changes happen:

- a new top-level subsystem or cross-cutting package boundary is introduced
- the frontend/backend communication model changes
- workspace layout or persistence placement changes
- desktop/browser/mobile responsibility boundaries move
- a fork-specific compatibility exception becomes an intentional RW Notes convention

## Planned v0 Architecture and Extension Boundaries

**Status: proposed design boundaries; implementation pending.** The agreed product target is one org per workspace, Admin/Write/Read roles, API/MCP agent collaboration, near-realtime connected updates, and offline-first desktop/mobile apps. Conflicts select the latest timestamp automatically and preserve the displaced version in recoverable history.

### Service, server kernel, and device responsibilities

| Component | Owns | Boundary to preserve |
| --- | --- | --- |
| Control plane (new) | Accounts, orgs, memberships, credentials, routing, provisioning, lifecycle, operator policy | Keep tenant/service concerns outside core content storage; one org/workspace per server kernel. |
| Kernel identity adapter (new) | Verified actor/workspace context, product-role mapping, authorization and revocation integration | Extend HTTP, WebSocket, static/file, and other exposed entrypoints consistently; no hosted fallback to universal access-code/admin credentials. |
| Collaboration adapter (new) | Operation identity, edit timestamps, dependency/revision information, conflict selection, durable history, ordered events, catch-up | Integrate at real mutation and commit boundaries; do not replace canonical `.sy` content or the editor model. |
| Server kernel (extended) | Accepted shared content, existing transactions, indexing, asset and database operations | Continue serializing authoritative writes; never rely on serialization alone to merge offline replicas. |
| Desktop/mobile local kernel (extended) | Local content replica, offline editing, durable pending queue, replay/catch-up | Preserve local native behavior while separating each org's content and credentials. Local save is not server acceptance. |
| Shared frontend (extended) | Existing editing/reading UI plus org/role, sync state, personal preferences, recoverable-conflict history | Reuse web/desktop/mobile code and preserve active local input on remote updates. |
| API/MCP adapter (new/extended) | Supported agent operations, credential context, observable outcomes | Use the same permission and reconciliation pipeline; no direct filesystem writes or bypass credentials. |

The planned connected flow is:

1. Authenticate a human or agent and bind a request/device to one org/workspace.
2. A native device persists its edit and pending operation locally; an online web/API/MCP client submits its mutation through the authorized interface.
3. The server validates current membership, operation identity, timestamp policy, and structural preconditions within the authoritative mutation ordering.
4. Non-conflicting changes are applied; conflicting changes select the timestamp winner. Preserve the losing version, whether it came from the server or the incoming operation.
5. Commit content and recovery metadata through a crash-recoverable mechanism. Acknowledge according to the documented durability boundary and publish an ordered event.
6. Other authorized clients apply or reconcile the event without destroying unsent input. A disconnected native device follows the same rules when it catches up.

This flow requires a design for consistency across file-backed content and separate metadata. A successful content write followed by a best-effort history/event write is insufficient. Prototype the journal/recovery boundary before broad client integration.

### Inherited vendor-service removal

v0 removes the current SiYuan cloud and related Liuyun/Liandi service integrations. This is an intentional compatibility exception: preserve reusable local primitives, but remove vendor-specific accounts, entitlements, payments, hosted sync/storage/publishing, API routes, background requests, configuration, and UI/native hooks. The detailed scope and release checks are in [saas-plan.md](./saas-plan.md).

Initial inventory locations include `app/src/config/account.ts`, `app/src/config/util/about.ts`, `app/src/mobile/settings/account.ts`, `kernel/model/updater.go`, and the cloud upload/export paths in `kernel/model/assets.go` and `kernel/model/export.go`. This list is a starting point, not a complete endpoint inventory; trace callers, routes, startup jobs, native purchase bridges, and service URL configuration too.

Audit update/package/resource delivery and any reporting dependencies so ordinary operation has no automatic calls or fallback to the removed services. Replace useful capabilities with explicitly chosen sources or retire them. Keep source attribution and user content intact. Local snapshots and provider-neutral storage adapters can remain when compatible with the new sync boundary; an upstream vendor account cannot remain a prerequisite. Validate clean and migrated profiles, including outbound traffic, after removal and future upstream merges.

### Configuration and storage boundaries

- Keep canonical content in upstream formats; use separately versioned durable metadata for service identities, user preferences, device queues, revisions, history, and replay.
- Split workspace policy, user-within-workspace preferences, and device/session state. Do not mass-move `data/storage` or broadcast personal writes to every member.
- `BoxConf.Closed` currently affects shared mount/index behavior. Add personal notebook visibility without letting a user's sidebar action unmount content for everyone.
- Keep service/provider secrets out of ordinary config responses. A Read member can update personal preferences without gaining content-write permission.
- Coordinate backups of content, memberships, and collaboration metadata. Full restore must invalidate obsolete replay cursors or use a new sync generation, while retaining pending client work for recovery.
- Do not run upstream snapshot/file sync as an independent second writer over a collaborative replica. Decide its allowed import/backup role explicitly.

### Compatibility and design review rules

- Prefer additive modules with small integration hooks. Document why any editor, transaction, storage, or native bridge change is necessary.
- Preserve IDs, block/reference semantics, database formats, import/export, and index rebuild behavior. Retain compatibility-sensitive internal naming without a planned forced rename.
- Audit every mutation path, including raw file routes, imports, restore, watchers, scheduled jobs, and plugins. Unsupported hosted operations must fail explicitly; supported ones must join the same permission/history/sync boundary.
- Classify events as workspace content, user-private, device/session, or operator-only before broadcasting them.
- Version client/server capabilities and define mixed-version behavior. An incompatible client must fail visibly instead of silently writing without required timestamp/history metadata.
- Track native wrapper/build dependencies outside this repository. A working `app/src/mobile` web build does not establish a shippable Android/iOS app.
- Test an upstream merge against storage, editor, API, native clients, and offline reconciliation fixtures. Record actual integration effort and keep a ledger of intentional divergence.

### Open architecture decisions

The SaaS plan owns the decision list and milestone gates. Highest priority: conflict unit (block/field/document), edit timestamp and clock-skew rules, structural conflict handling, recoverable-version retention, durable journal placement, identity provider, and native platform matrix. No CRDT/OT engine, new content database, or exact control-plane stack is selected by this document.

Later v1 notifications, summaries, and Todoist-like database workflows should consume stable content IDs and versioned authorized events. They should not force speculative changes into the v0 editor or content model.
