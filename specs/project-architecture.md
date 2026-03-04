# Project Architecture

This document describes how RW Notes is put together so future agents can find the correct layer before changing behavior.

It is intentionally practical rather than exhaustive. When the architecture changes materially, this file should be updated in the same change.

## Fork Context

- This repository is a fork of SiYuan and still keeps many internal compatibility identifiers as `siyuan`.
- User-facing naming should follow [name-and-look-and-feel.md](./name-and-look-and-feel.md).
- Internal names such as protocol handlers, config paths, environment variables, Go module paths, Electron IPC channel names, and some runtime globals may still use upstream naming. Do not mass-rename those unless explicitly told to.

## Top-Level Shape

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

- `kernel/main.go` is the non-mobile kernel entrypoint.
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
- optional push notification back to clients via WebSocket

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
- The workspace is single-writer guarded by a lock file.

## Communication Patterns

### HTTP API

- Most client mutations and reads go through `POST /api/...`.
- `kernel/api/router.go` is the main registration point.
- Authentication, role checks, and read-only checks are applied in the API layer before reaching business logic.

### WebSocket

- `/ws` is used for live UI updates, reloads, progress, sync notifications, and some command-style messages.
- `app/src/layout/Model.ts` is the main client-side abstraction for WebSocket connections.
- Kernel pushes are important for keeping multiple windows/sessions coherent. If a backend change mutates visible state, check whether a push/reload message is also needed.

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
