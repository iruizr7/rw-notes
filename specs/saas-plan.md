# SaaS Plan

RW Notes is intended to grow into a SaaS product in the same broad category as Notion. This document captures the current architectural assessment and the recommended path for reaching a viable first SaaS version.

It is intentionally scoped to the first credible SaaS milestone, not the final product shape. Later iterations can expand this into a fuller RFC covering tenancy, billing, deployment, and collaboration details.

## Product Goal

The long-term SaaS direction assumes:

- multiple authenticated users per workspace
- workspace-level roles such as admin, editor, and reader
- user-specific preferences and UI state

This is high complexity but feasible.

If the target also includes the following in the first step, the scope becomes much larger:

- private notes inside one shared workspace
- notebook-level or document-level ACLs
- polished Google Docs style real-time collaboration

Those capabilities are not a good first SaaS step for this codebase.

## Current Architectural Assessment

The current repo is still primarily architected as one kernel process serving one workspace with one effective admin identity.

### Workspace Model

- The kernel is single-workspace by design. Workspace paths and DB locations are global process variables in `kernel/util/working.go` and boot wires one global config plus one set of DBs in `kernel/main.go` and `kernel/sql/database.go`.
- The current `--workspace` model already aligns better with one workspace per kernel instance than with many workspaces inside one shared process.

### Authentication And Identity

- Authentication is effectively based on one shared workspace access code. `LoginAuth` checks one shared `Conf.AccessAuthCode` and stores only that in session state in `kernel/model/session.go` and `kernel/util/session.go`.
- The normal workspace auth flow does not model distinct users.
- `CheckAuth` promotes any valid session or access-code holder to administrator in `kernel/model/session.go`.
- The only existing named-account system is for the publish reverse proxy, not for the workspace itself. It creates JWTs with `RoleReader` in `kernel/model/auth.go`, and the proxy injects them in `kernel/server/proxy/publish.go`. This can be reused as a starting point, but it is not a finished multi-user model.

### Shared Versus Personal State

- The frontend boots from one workspace-wide config blob returned by `/api/system/getConf` in `kernel/api/system.go`.
- That config object mixes shared system state and personal UI state in one `AppConf` type in `kernel/model/conf.go`.
- Several data files that appear user-local are actually stored as shared workspace state under `workspace/data/storage`, including `recent-doc.json`, `criteria.json`, `local.json`, and `outline.json`, managed in `kernel/model/storage.go`.
- The client loads that storage directly into `window.siyuan.storage` in `app/src/protyle/util/compatibility.ts`.
- Notebook open and closed state is also shared. `GetOpenedBoxes()` uses notebook `Closed` flags globally in `kernel/model/conf.go`, and mount or unmount persists that in `kernel/model/mount.go`. One user opening or closing notebooks would affect everyone.

### Concurrency And Collaboration

- Writes are intentionally serialized. There is request-path level write serialization in `kernel/model/session.go`, and transactions are funneled through a single queue in `kernel/model/transaction.go`.
- This protects integrity, but it will bottleneck under many concurrent editors.
- WebSocket push is session-aware and window-aware, not user-aware. Transaction pushes carry app and session in `kernel/api/transaction.go`, while WebSocket auth in `kernel/server/serve.go` only checks the workspace cookie or publish JWT.
- There is no per-user filtering, presence, or user-scoped broadcast model.
- There is no visible CRDT, OT, or presence layer. The current model is serialized mutations plus broadcasts and reloads, not true collaborative editing.
- For an MVP, coarse collaboration may be acceptable if the product explicitly accepts last-write-wins behavior plus refreshes.

### Content Ownership And Permissions

- The content and index schema has no user ownership or ACL dimension.
- Core tables such as `blocks` are created without owner fields in `kernel/sql/database.go`.
- That is workable for fully shared workspaces, but not for private content or fine-grained permissions inside a workspace.

## First SaaS Target

The safest first SaaS interpretation is:

- one workspace equals one tenant or organization
- all content inside that workspace is shared
- roles are workspace-wide
- per-user preferences and UI state are separated from workspace state
- there are no per-document ACLs initially
- there are no strong real-time collaboration guarantees initially

This target is meaningful and avoids the worst redesign pressure.

### Explicit Non-Goals For The First SaaS Milestone

The initial SaaS milestone should not attempt to deliver:

- many workspaces inside one kernel process
- per-block or per-document ACLs
- SaaS auth layered on top of the current access-code model without a proper user model
- Electron as a first-class requirement for the SaaS MVP

### Recommended Architecture Path

#### Deployment Model

- Keep the kernel single-workspace per process.
- For SaaS, provision one kernel instance or container per workspace and place a control plane in front of it.

#### Control Plane Responsibilities

Build users, workspaces, and memberships outside the kernel first. The SaaS control plane should own:

- email and OAuth authentication
- billing
- invitations
- workspace creation
- routing
- lifecycle management

#### Kernel Authentication Integration

- Extend kernel auth so it can trust an external signed JWT or an internal gateway header carrying at least `workspace_id`, `user_id`, and `role`.
- The JWT middleware in `kernel/server/serve.go` is a reasonable insertion point.
- The current publish JWT model is too limited to serve as the full workspace auth system.

#### Configuration Split

The current configuration model must be split into workspace-scoped state and user-scoped state.

Workspace or admin config should include:

- sync
- repo
- publish
- API token
- AI provider
- system and network settings
- snippets
- notebooks
- shared content

User config should include:

- appearance
- language
- keymap
- layout
- recent docs
- search criteria
- outline expansion
- dialog positions
- local history
- search history

#### User-Scoped Storage

- Data currently stored under `data/storage/*.json` should move to user-scoped storage.
- The simplest first move is likely `data/storage/users/<userId>/...` or a new metadata table keyed by `user_id`.

#### Notebook State

- Notebook open or closed state should be treated as personal state in SaaS.
- The current `BoxConf.Closed` model cannot remain unchanged if different users must manage their own notebook visibility.

#### Roles

- Real workspace roles must exist in the normal auth path.
- `admin`, `editor`, and `reader` already exist in `kernel/model/role.go`.
- The missing piece is binding real users to those roles for workspace access.

#### Auditability

- Audit logging should be added early.
- In a SaaS product, tracking who changed what becomes important before fine-grained ACLs are introduced.

#### Collaboration Scope

- Collaborative editing should be treated as a separate track.
- The existing transaction queue may be sufficient for a small-team MVP with coarse conflict behavior.
- It is not sufficient for polished live collaboration.

## Effort Estimate

For one experienced engineer working full-time, rough order-of-magnitude estimates are:

- shared workspace membership with admin, editor, and reader roles, web auth, and no user-specific preferences: 3 to 6 weeks
- shared workspace membership plus a proper per-user preferences and state split: 6 to 10 weeks
- a real SaaS MVP around this repo, including workspace provisioning, auth, routing, backups, observability, admin UX, member management, and deployment: 3 to 6 months
- per-document permissions or polished real-time collaboration: an additional 3 to 9 or more months, depending on ambition

The main constraint is not only multi-user authentication. The deeper challenge is that the current codebase stores a large amount of UX and configuration state as if the workspace had a single user.

## Recommended First Milestone

The first SaaS milestone for this fork should be:

- web-first SaaS
- one kernel instance per workspace
- workspace members with shared content
- admin, editor, and reader roles
- per-user UI state extracted from shared workspace storage
- no per-document ACL yet
- no Electron requirement for the MVP

This is a defensible architecture direction and fits the current codebase without forcing an unnecessary full redesign upfront.
