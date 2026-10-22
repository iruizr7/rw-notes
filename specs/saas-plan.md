# RW Notes: Product Objectives and SaaS Plan

Updated: 2026-10-22.

This is the product and delivery plan for RW Notes. It supersedes the earlier web-first SaaS MVP proposal. **v0 includes near-realtime collaboration, API/MCP agents, desktop and mobile apps, and offline-first device editing.** These are release requirements, not optional follow-up work.

This document distinguishes **agreed product decisions** from **proposed implementation choices** and **open decisions**. None of the target capabilities below should be read as already implemented. See [project-architecture.md](./project-architecture.md) for the current code and intended extension boundaries, and [name-and-look-and-feel.md](./name-and-look-and-feel.md) for branding.

**Selected upstream baseline:** core and Android 3.8.8, with iOS commit `05280f32ba89705e3ba55c233037db02c93cdea8`. See [upstream-baseline.md](./upstream-baseline.md) for exact SHAs, provenance limits, branch policy and validation gates. Source alignment is an M0 prerequisite, not completion of M0.

## 1. Vision and Terms

RW Notes aims to offer a Notion-like shared knowledge service built on SiYuan: multiple people and AI agents work in one organization's knowledge base, with near-realtime updates across the web, desktop, and mobile. Desktop and mobile retain useful offline operation. “Notion-like” describes the shared service experience; it does not require replacing SiYuan's editor, storage model, or UI.

| Term | Meaning in this project |
| --- | --- |
| Upstream | The official SiYuan repository, `siyuan-note/siyuan`. It never means the RW Notes fork or its `origin` remote. |
| RW Notes | This fork and its additional service, identity, collaboration, and client integration components. |
| v0 | The first planned functional increment over upstream: shared organizations/workspaces, Admin/Write/Read access, human/agent collaboration, and offline-capable desktop/mobile participation. Existing branding work is not completion of v0. |
| v1 | A later increment, provisionally including notifications, summaries, and Todoist-like task/project management on databases. Its scope is not committed yet. |
| Organization / org / tenant | The membership and isolation boundary. In v0, exactly one org equals exactly one workspace. |
| Workspace | The complete shared knowledge base and its content, assets, databases, configuration, and history. All org members can read all workspace content. |
| Notebook | A content container inside a workspace, not a tenant or permission boundary. |
| User | An individually authenticated human with a workspace membership. One account may have memberships in multiple independent orgs; there is no cross-org content access by implication. |
| Agent | An individually attributable automation identity, or a credential explicitly delegated by a user, operating through API or MCP. It is subject to workspace permissions. |
| Role | Exactly one of **Admin**, **Write**, or **Read** for a membership, applying to the whole workspace. |
| Collaboration | Humans and agents changing the same shared knowledge base, with permission checks, automatic propagation, attribution, and defined conflict behavior. |
| Near-realtime | Connected clients receive committed changes automatically within a measured latency target; no manual refresh or scheduled bulk sync is needed for ordinary edits. |
| Offline-first | Desktop/mobile maintain local content and can edit while disconnected, then reconcile with the shared workspace on reconnect. |
| Reconciliation | Applying queued local changes and remote changes according to the timestamp conflict policy, with recoverable displaced versions. |
| Sync | RW Notes collaboration/reconciliation unless explicitly called **upstream snapshot/file sync**. These are different mechanisms. |
| Database | A user-facing SiYuan attribute-view database, unless explicitly called a SQLite index or service metadata database. |

RW Notes release milestones are separate from upstream version numbers. Each release must identify both its RW Notes version and the upstream commit/version it incorporates.

## 2. Agreed Product Decisions

1. v0 supports multiple authenticated users per org, with **org = workspace**.
2. Roles are workspace-wide **Admin**, **Write**, and **Read**. No private notes or notebook/document/block ACLs in v0.
3. Web users, AI agents using API or MCP, desktop apps, and mobile apps collaborate in the same knowledge base.
4. Connected clients synchronize near-realtime. A web-only milestone may be an internal checkpoint, but cannot be called completed v0.
5. Desktop and mobile are offline-first: local editing continues while disconnected and reconciles later. Offline web editing is not a v0 requirement.
6. When concurrent changes conflict, **the latest timestamp wins automatically, with the displaced version recoverable in history**. Manual conflict resolution is not required before ordinary sync can proceed.
7. Preserve upstream core code as far as practical, aiming for low to medium effort when integrating future upstream improvements and releases.
8. Prioritize the existing storage format, editor, and shared web/desktop/mobile UI. Add service and collaboration capabilities around those foundations.
9. Remove all inherited SiYuan cloud and related vendor-service integrations from the RW Notes product in v0, including Liuyun (`liuyun.io`), Liandi (`ld246.com`), and their account, subscription, payment, sync, storage, and publishing flows. RW Notes must operate independently of those services.
10. v1 candidates include email and push notifications, summaries, and **Todoist-like task/project management built on RW Notes databases**. A Todoist service integration is not currently requested.

Timestamp conflict resolution deliberately favors automatic progress over preserving every edit in the visible winning content. Recoverable history is therefore part of correctness, not optional polish. File timestamps alone do not define a sufficient distributed conflict protocol; timestamp source, ordering, conflict scope, and history durability must be specified before implementation.

## 3. Upstream Compatibility Objectives

Preservation is a design constraint, not a promise that unmodified upstream clients can join a collaborative RW Notes workspace. Required authentication, revision, and reconciliation extensions will need compatible RW Notes clients.

| Compatibility surface | v0 objective |
| --- | --- |
| Canonical storage | Retain upstream document/block trees, `.sy` files, assets, notebook layout, and attribute-view data formats. Avoid a content-store rewrite. |
| Identity and links | Retain stable notebook/document/block IDs, references, backlinks, embeds, asset paths, and link semantics. |
| Editor and content semantics | Reuse Protyle and the existing parsing/rendering pipeline, supported block types, transactions, and database operations. Add narrow synchronization hooks. |
| Shared UI | Reuse existing web, Electron, and mobile surfaces. Add organization, member, sync, and history affordances without rebuilding the application. |
| APIs and extensions | Preserve existing content API shapes where feasible. Explicitly version additional auth/sync contracts and document permission changes. Evaluate plugins, themes, widgets, and snippets under the hosted permission boundary. |
| History, import/export, and search | Preserve portable content, history/snapshot workflows, indexing, and backup/restore behavior; verify links and database relations after recovery. Collaboration history supplements upstream history where needed. |
| Desktop/mobile integration | Preserve native bridges, packaging, protocols, filesystem assumptions, and local-kernel behavior where compatible. Inventory external native wrapper sources and build dependencies early. |
| Runtime identity and builds | Retain compatibility-sensitive module names, paths, environment variables, IPC names, and globals. Keep target-specific boot/build paths working. |

Upstream cloud/vendor-service integrations are an explicit exception to preservation: remove their runtime dependencies and product surfaces while retaining reusable local storage, editor, UI, and snapshot primitives. Compatibility must not become a reason to retain upstream accounts or service calls.

Prefer separate modules and adapters for identity, membership, service metadata, collaboration envelopes, and transport. Keep necessary upstream edits localized and justified. Avoid putting required identity, history, or synchronization state solely in rebuildable content indexes under `temp/`.

Maintain a compatibility ledger recording touched upstream surfaces, rationale, tests, and migration requirements. At each upstream integration, record conflict hotspots and actual effort. For planning, **low effort** means routine merges and verification without architecture changes; **medium effort** means localized adapter changes and bounded migrations. Repeated core/editor/storage redesign is **high effort** and triggers an architecture review. This is a maintenance target to measure, not an estimate guaranteed in advance.

## 4. Current Repository Assessment

The table below is the **historical 3.5.8 assessment** reviewed at commit `abba74f34`. The selected baseline is now 3.8.8; M0 must refresh this inventory before using it as an implementation map. In particular, upstream now has typed API contracts, built-in MCP/agent facilities and revised configuration accessors. Their presence does not establish RW Notes organization permissions or offline collaboration.

| Area | Existing foundation | Work required for v0 |
| --- | --- | --- |
| Workspace | Global workspace/config/DB paths in `kernel/util/working.go`, `kernel/main.go`, and `kernel/sql/database.go`; one workspace per kernel process. | Keep process isolation and add external org provisioning/routing. |
| Identity | `kernel/model/session.go` authenticates a shared access code or API token; those paths assign administrator privileges. Publish accounts/JWTs in `kernel/model/auth.go` are a separate facility. | Bind real identities and memberships to requests and sockets. Shared workspace credentials cannot authorize hosted users. |
| Roles | `kernel/model/role.go` provides `RoleAdministrator`, `RoleEditor`, and `RoleReader`. `kernel/api/router.go` applies admin checks to many content and preference routes. | Map product roles and audit every exposed capability; assigning a role alone is insufficient. |
| Personal state | `AppConf` in `kernel/model/conf.go` mixes state; `kernel/model/storage.go` writes shared recent-doc, criteria, local, and outline files. | Separate workspace, user, and device state and their broadcasts. |
| Notebooks | `BoxConf.Closed` and mount/unmount operations affect the shared kernel. | Separate personal visibility from actual shared mount/index lifecycle. |
| Mutation pipeline | `kernel/model/transaction.go` queues writes; `kernel/api/transaction.go` broadcasts transaction results using app/session IDs. | Preserve serialization while adding identity, durable ordering, conflict handling, retry safety, and recovery. Serialization alone does not reconcile independent offline edits. |
| Live transport | `kernel/server/serve.go` and `app/src/layout/Model.ts` provide WebSocket plumbing. | Add authenticated workspace/user/device context, authorized event delivery, replay/catch-up, and client convergence. |
| Clients | `app/electron/main.js`, `app/src/mobile/`, and `kernel/mobile/kernel.go` provide desktop/mobile integration points. | Prove local replicas, identity, background/resume behavior, and packaging on actual target apps. Mobile web alone is insufficient. |
| Agent access | Existing HTTP content APIs provide an integration base. | Define the supported API/MCP tool set, scoped credentials, mutation envelopes, history, and observable outcomes. |

These are extension points, not proof that multi-user collaboration already works. The main risks are concurrent/offline edits, shared personal state, and legacy routes that assume one trusted administrator.

## 5. v0 Functional Contract

### Remove inherited cloud and vendor services

This is a v0 deliverable across web, desktop, mobile, and kernel code, not merely a branding change or hidden settings panel.

- Inventory and remove SiYuan cloud, Liuyun, Liandi, and related vendor account login/registration, account binding, cloud-region selection, subscriptions, purchase/renewal/donation prompts, payment and native purchase callbacks, and vendor entitlement checks. Product capabilities must not depend on a SiYuan subscription; any future RW Notes commercial policy is separate.
- Remove their hosted sync, cloud snapshots/backups, storage/quota management, cloud asset uploads, publishing/export integrations, and associated API routes, background jobs, persisted credentials, and configuration surfaces. RW Notes identity, collaboration, and backup workflows take over the corresponding product responsibilities.
- Audit all remaining automatic vendor requests and bundled remote dependencies, including update checks/download mirrors, service discovery, marketplace/package retrieval, remote resources, and telemetry/reporting where present. Remove inherited service integrations; any retained capability must use an explicitly chosen RW Notes or independent source, with no silent fallback to the removed services.
- Remove obsolete UI, promotional links, active help/setup instructions, translations, and native hooks tied to those services. Preserve source attribution, license notices, historical changelogs, and user-authored content/links.
- Migrate existing workspaces without deleting local notes, assets, or snapshots. Stop using inherited vendor credentials and remove obsolete credential/config fields through a documented migration. Do not delete users' remote accounts or cloud data. Document how users bring down cloud-only content before switching; do not imply it has been migrated automatically.
- Preserve generic local snapshot/import/export machinery and provider-neutral protocols such as S3/WebDAV where useful and compatible with RW Notes policy. Their existence does not authorize retaining SiYuan-operated services or running an independent sync writer over a collaborative replica.
- Verify clean installs and migrated profiles with the removed services unavailable. Startup, editing, offline use, collaboration, and backup/restore must not require those accounts, licenses, or endpoints. Check outbound traffic and obsolete routes as well as visible settings. Repeat this check after upstream merges to prevent reintroduction.

M0 produces the service/endpoint inventory and replacement map; M1–M2 remove vendor identity, entitlement, routes, and background dependencies; M6 completes client/native cleanup; M7 verifies independence across all release targets. Removal is agreed scope; exact replacements for useful capabilities are design decisions.

### Membership and roles

Use the product names **Admin**, **Write**, and **Read** in new UI and specifications. Existing internal constants may remain `RoleAdministrator`, `RoleEditor`, and `RoleReader` respectively to reduce upstream divergence.

| Capability | Admin | Write | Read |
| --- | --- | --- | --- |
| Read/search shared content, assets, and database views | Yes | Yes | Yes |
| View recoverable content conflict versions | Yes | Yes | Yes |
| Create/edit/move/delete ordinary content and database records | Yes | Yes | No |
| Restore a displaced content version as a new edit | Yes | Yes | No |
| Change own preferences and device UI state | Yes | Yes | Yes |
| Manage members, roles, and workspace agent credentials | Yes | No | No |
| Change shared workspace policy and approved integrations | Yes | No | No |
| Restore an entire workspace or perform destructive workspace maintenance | Yes, through controlled workflows | No | No |
| Operate the host, arbitrary filesystem, shell, or service infrastructure | No implicit access | No | No |

Prevent removal/demotion of the last Admin without transferring administration. Define membership addition/removal, credential revocation, and role changes across HTTP, sockets, and reconnecting devices. A revoked device cannot submit or fetch further changes; already downloaded offline data cannot be remotely unread.

Read users can update their own preferences even though shared content is read-only. Admin is an org role, not a service-operator role. Review raw file, SQL/query, DAV, upload/export, plugin, proxy, sync, and configuration routes as well as normal content endpoints. Unsupported hosted routes must fail explicitly rather than provide alternate mutation paths.

### Collaboration and offline reconciliation

The following is the required behavior; the exact protocol remains an implementation decision:

1. Each client/agent has a stable actor identity; devices and individual operations have stable IDs. The server derives identity and workspace from verified credentials, not request-body claims.
2. Local desktop/mobile edits are durably stored with a pending-operation record before the app reports them as saved locally. Local save and shared synchronization are distinct states.
3. All supported shared mutations participate: text, blocks, document/notebook structure, attributes, database records/schema, and assets. Any operation temporarily unavailable offline is explicitly inventoried and agreed before the v0 scope is frozen; workspace membership/admin changes require connectivity.
4. Connected changes propagate automatically. Incoming events must preserve in-progress local input, selection/composition, and pending edits rather than replace an active editor blindly.
5. On reconnect, clients exchange missing changes and replay queued operations idempotently. Both non-conflicting offline changes and server changes are retained.
6. For conflicting edits, the greatest agreed timestamp determines the winner. Equal timestamps have a deterministic secondary order. A late-arriving old edit must not overwrite a newer winner merely because it arrived later.
7. Store the displaced version durably before acknowledging a conflict as reconciled. If the incoming edit loses, preserve that incoming version too. Retries must not produce duplicate effects or duplicate conflict records.
8. History identifies both versions, actors/devices, timestamps, and the selected winner. Restoring an older version creates a new authorized operation; it does not reset shared history or erase later changes.
9. Deletions need retained deletion records (tombstones) and recoverable content. Define edit-versus-delete, move-versus-edit, parent/child, and database schema-versus-record conflicts. Timestamp ordering must still produce structurally valid content without dangling references introduced by partial application.
10. Membership and role checks run again when offline operations reach the server. A formerly writable device cannot bypass a later downgrade. Keep rejected local work recoverable and show that it was not shared.
11. Recovery covers duplicate requests, interrupted asset uploads, socket gaps, restarts, and crashes between content persistence, history persistence, and event publication. Clients can recover through replay or a consistent snapshot plus remaining changes.
12. Shared undo must not silently roll back another participant's unrelated work. Define it as a new operation against current shared state, with the same timestamp/history rules.

Do not equate near-realtime collaboration with simultaneous character-level merging. v0 explicitly chooses automatic timestamp conflict resolution with history. CRDT/OT adoption is not assumed; any proposal must demonstrate a benefit worth its effect on storage/editor compatibility.

### Timestamp and conflict design gate

Before building the full protocol, prototype and document:

- **Conflict unit:** prefer block/field-level conflicts where safe; compare the cost with document-level replacement. A whole-document winner can displace unrelated edits, so this granularity must be explicitly accepted, not hidden in implementation.
- **Timestamp source:** choose how offline edit times, device clock skew, backward clocks, future-dated edits, and untrusted agent timestamps are handled. Server receipt time alone does not represent offline edit time. Define an accepted skew policy, deterministic tie-breaking, and visible handling of invalid timestamps; never silently discard pending work.
- **Detection and ordering:** timestamps select the winner; base revisions/dependencies identify what actually conflicts. An ordered server event cursor supports delivery and replay independently of the winning edit's timestamp.
- **Consistency boundary:** specify atomic operations for document moves, notebook operations, database schema changes, and asset references; preserve upstream structural invariants.
- **History and retention:** decide storage, retention, pruning of tombstones, maximum supported offline interval, and full-resync behavior for devices older than retained history. Expired replicas must not resurrect deleted content. Retain their pending edits for reconciliation or recovery.
- **Durability:** demonstrate recovery when file-backed content and separate collaboration metadata cannot be committed in one database transaction. Use a recoverable journal or equivalent mechanism; a content write followed by best-effort history is insufficient.

The user has agreed the winning policy, not these implementation details. Clock skew means “latest” needs a published definition; accurate real-world edit order cannot be inferred from unchecked device clocks.

### API and MCP agents

Provide both a supported HTTP API path and an MCP adapter for reading/searching and editing shared knowledge. The adapter uses the same authorization, timestamp/conflict, durable history, and mutation pipeline as human clients. It must not write workspace files directly or use a universal administrator token.

Initial operations should cover document/block reads and edits, search, attributes, assets, and database rows. Publish a capability table showing supported operations, required role, retry behavior, conflict outcomes, and error responses. Broader upstream APIs are not automatically safe or supported for hosted access.

Credentials are individually revocable and workspace-scoped. Record the initiating human when an agent acts by delegation; delegated access cannot exceed that user's current role. Service agents have explicit membership/role policy. Default agent creation to Read or Write as appropriate; Admin is not necessary for ordinary knowledge work.

API/MCP callers must be able to distinguish accepted/synchronized, pending, rejected, superseded, and retryable outcomes. Enforce rate/size limits and backpressure so an agent cannot starve interactive users. Agents need a supported way to observe changes and reconciliation results; the exact subscription/polling interface is open.

### Personal state and client experience

| Scope | Examples | Intended behavior |
| --- | --- | --- |
| Workspace | Content, assets, database definitions/shared views, approved snippets/plugins, shared provider configuration | Shared and permission controlled; secrets omitted from ordinary client config. |
| User within workspace | Recent documents, saved searches, notebook visibility, outline expansion, preferences | Private to the user; selectively synchronized across their devices. |
| Device/session | Window geometry, device paths, transient tabs where appropriate, platform shortcuts, credentials, pending-operation queue | Local or device-keyed; never broadcast to other members. |
| Service | Memberships, credential records, routing, quotas, operator settings | Managed outside canonical content; inaccessible through ordinary content APIs. |

Classify every existing config/storage key before migration. Do not move all `data/storage` files indiscriminately. Shared database view definitions remain shared; purely personal view state must be identified separately. Notebook hiding must not unmount content needed by other users or agents. Seed legacy personal state only into the designated migrating owner, not every member.

The UI must show current org and role, connected/offline state, locally saved versus synchronized state, pending/rejected operations, and automatic conflict resolution with a link to recoverable history. Notification banners and sync status in v0 are separate from v1 email/mobile push delivery.

## 6. Proposed Architecture

These are preferred starting choices to validate in the discovery milestone, not implemented components:

- **One authoritative server kernel per workspace**, with its own volume and existing single-workspace process model. Avoid many tenants inside one kernel.
- **An external control plane** owns users, memberships, identity-provider integration, org creation, routing, credentials, quotas, and lifecycle management. Automated billing is not necessary for the first pilot.
- **A narrow kernel auth adapter** verifies signed workspace/actor credentials and maps roles into existing helpers. Validate issuer, audience, workspace, expiry, and revocation. A gateway header is trusted only over an authenticated internal boundary that strips client-supplied equivalents. Hosted kernels must not retain shared-token/access-code/localhost fallback paths that bypass org identity.
- **A collaboration adapter at mutation/commit boundaries** supplies operation IDs, timestamps, revisions, durable history, event cursors, and replay. Keep upstream content transactions and rendering as the foundation. Inventory bypass paths such as import, restore, filesystem watchers, and background jobs.
- **Desktop/mobile local kernels and replicas** retain upstream-compatible content and persist pending operations. The server is authoritative for accepted shared state; local devices remain authoritative only for their unsynchronized work until accepted or superseded. Do not share one writable volume between independent kernels.
- **Separate durable service/collaboration metadata** stores identity, personal state, operations, and recoverable versions outside canonical content formats and rebuildable indexes. Exact database, placement, and backup coordination are open. Local device queues need their own durable storage too.
- **Existing HTTP/WebSocket foundations plus versioned sync extensions** carry live updates and catch-up. Existing upstream snapshot/file sync must not independently overwrite the same collaborative replica. Define whether it is disabled for shared workspaces or used only through controlled import/backup workflows.
- **An MCP adapter over supported APIs** makes agent access attributable and consistent without duplicating mutation rules.

Retain standalone local operation as a regression target where feasible. Hosted mode and standalone mode need explicit configuration boundaries. Content compatibility does not imply that upstream understands RW Notes memberships, conflict history, or operation logs; portable content export and full service restore are separate capabilities.

## 7. Delivery Milestones

Implement in small increments, each leaving a demonstrable system. The sequence is dependency-driven, not a calendar commitment. Desktop/mobile feasibility work starts in M0 rather than waiting for a finished web service.

| Milestone | Dependencies | Deliverables | Exit evidence |
| --- | --- | --- | --- |
| **M0 — Baseline and risky-path prototypes** | None | Pin and validate the selected 3.8.8 core/Android and iOS commit combination; refresh the historical 3.5.8 inventory; inventory routes/config/mutations and inherited vendor services/endpoints; locate native app sources and build requirements; prototype two clients plus one agent editing online/offline; decide timestamp/granularity/history design; define load and latency targets. | Demonstrate concurrent edits, offline reconnect, displaced-version recovery, and one native client path without changing canonical storage. Record unresolved design decisions and implementation estimates. |
| **M1 — Organization and deployment boundary** | M0 topology decisions | Control-plane user/org/membership model; one kernel/volume per org; provisioning, routing, service health, backup skeleton; first identity-provider flow and admin/member UI; replace inherited vendor identity and entitlement dependencies. | Create two orgs; route each to isolated content; restart without losing membership; verify cross-org denial. Use admin-mediated provisioning or invite links if email delivery is deferred. |
| **M2 — End-to-end identity and roles** | M1 | Kernel auth adapter; API/socket/static-route permission inventory; Admin/Write/Read enforcement; individual agent credentials; revocation and last-Admin protection; remove vendor-service routes, credentials, and background calls. | Exercise all three roles through web/API/MCP; verify private user state and secrets stay private, Read cannot mutate shared content, and removed identities cannot reconnect. |
| **M3 — Personal state migration** | M2 | Scope config/storage keys; separate user/device state; personal notebook visibility; migration and rollback procedure. | Two users and two devices use distinct preferences with no cross-user leakage; Read can save preferences; hiding a notebook leaves it accessible to others. |
| **M4 — Connected collaboration and agent access** | M0 conflict design, M2–M3 | Durable mutation envelope/history, timestamp conflict handling, event cursor/catch-up, idempotency, editor update integration, supported HTTP and MCP operations. | Web clients and multiple agents converge without manual refresh; deterministic conflicts recover both versions; retries/restarts preserve accepted work; latency measured under agreed load. |
| **M5 — Offline reconciliation** | M4; M0 native/local-replica proof | Durable device queues, local save state, missing-event exchange, asset transfer, deletion handling, permission recheck, stale-replica recovery, clock policy. | Two disconnected writers edit the same and different content, then reconnect in both orders; all replicas select the same winner and expose displaced history. Fault-injection and role-downgrade cases pass. |
| **M6 — Desktop/mobile delivery** | M3–M5; native work starts in M0 | Shared identity/sync integration in desktop and mobile apps; account/org switching; safe local-cache separation; native packaging; resume and connection-loss UX; remove remaining vendor account/payment/cloud UI and native hooks. | Demonstrate web + desktop + mobile + API/MCP together on agreed OS targets, including app termination, offline restart, and reconnect. A mobile browser demonstration alone does not pass. |
| **M7 — Pilot and upstream integration rehearsal** | M1–M6 | Operational limits/metrics, backup+restore, migrations, client protocol compatibility, pilot runbook, upstream merge rehearsal and compatibility ledger. | Complete the acceptance matrix below, restore a real test org, verify pending-client recovery after restore, measure merge effort, and close release-blocking gaps. |

Every milestone should produce an updated spec/decision record, implementation tasks with dependencies, and acceptance evidence. Do not repeat the earlier 3–6 week membership or web-only MVP estimates as estimates for this v0. Offline multi-client reconciliation and native delivery materially expand that scope. Estimate work after M0 validates the risky paths; avoid dates based solely on auth implementation effort.

## 8. v0 Acceptance Matrix

| Scenario | Release requirement |
| --- | --- |
| Roles and tenancy | Admin, Write, and Read behave consistently across web/native/API/MCP; no org crossing via content, assets, history, sockets, or raw routes. |
| Connected editing | At least two human clients and two agents contribute; other connected clients update automatically and retain active local input. |
| Same-content conflict | Timestamp winner is deterministic regardless of delivery order; losing local or remote version is durably recoverable, attributable, and restorable. |
| Independent edits | Non-conflicting edits survive reconciliation; measured conflict granularity and its overwrite consequences are documented. |
| Structural operations | Move/delete/restore, notebook changes, database row/schema changes, and asset references yield valid content and recoverable losses. |
| Offline devices | Desktop and mobile reopen while offline, retain saved changes, then catch up/reconcile on reconnect without duplicate effects. |
| Clocks and stale replicas | Equal/future/backward clocks, duplicate operations, and replicas older than retention follow documented policy and preserve recoverable local work. |
| Access changes | Revoked/downgraded devices lose remote access/write rights, including queued edits; rejected work remains visible locally for recovery. |
| Personal state | Other users cannot read or overwrite personal preferences/history; device-specific paths/window state do not leak or break other platforms. |
| Durability | Crash/restart at commit/history/event boundaries does not lose acknowledged changes or the promised displaced versions. |
| Recovery | Coordinated content + metadata backup restores identities, winning state, conflict history, and a safe reconnect path. Restores use a new sync generation or equivalent protection against obsolete cursors. |
| Compatibility | Representative documents, links, assets, database views, search, import/export, and builds pass after an upstream merge; content portability is verified against a specified compatible upstream build on a separate copy. |
| Vendor-service independence | Clean and migrated installations work with SiYuan/Liuyun/Liandi services unavailable; no inherited automatic service calls, credential use, purchase flows, or vendor entitlement requirements remain. Repeat after upstream merges. |
| Performance | Publish measured connected-update latency, reconnect time, backlog behavior, and resource use against a reproducible workspace/load fixture. |

**Proposed initial benchmark, to confirm in M0:** p95 remote visibility within 2 seconds of server commitment for ordinary edits, with 10 connected human clients and 2 active agents per workspace under a documented network/load profile. Measure local-edit-to-remote-visible latency separately so batching does not hide delays. Large assets/imports use progress reporting and separate throughput targets. Offline time and mobile OS suspension do not count as connected latency; catch-up after resume does. This is a test target, not an agreed SLA or a current performance claim.

## 9. Scope Boundaries and Later Work

Not required for v0:

- Multiple workspaces inside one org or one multi-tenant kernel process.
- Private notes or notebook/document/block permissions inside an org.
- Character-level conflict merging, guaranteed preservation of every edit in the visible winning text, or polished remote cursors/presence.
- Offline browser editing, automatic billing, or a complete self-service commercial launch.
- A new content format, editor rewrite, or general UI redesign.
- Full protocol compatibility with unmodified upstream apps.
- Email notifications, mobile push notifications, scheduled summaries, or a task/project-management layer.

Minimal identity and member onboarding are v0 requirements; they must not depend on building the v1 notification platform. Email delivery for login or invitations, if chosen, is a separately scoped identity dependency rather than an implicit commitment to that platform.

Likely v1 exploration:

- Email and push delivery for relevant activity, reminders, and changes.
- User-controlled summaries of shared knowledge and activity, with source references and workspace permissions.
- Todoist-like tasks/projects built on existing databases: candidate fields include status, assignee, priority, due date, recurrence, and project; candidate views include personal work and project overviews.
- More sophisticated collaboration/presence if use warrants it, assessed against upstream maintenance cost.

v0 should preserve stable content IDs, actor attribution, a versioned event interface, and database compatibility so these extensions have a foundation. Do not build their business rules speculatively into the core or turn a short-lived sync replay log into an assumed permanent notification store.

## 10. Decisions Still to Make

The vision, role names, offline-first requirement, timestamp-winner-with-history policy, and removal of inherited cloud/vendor-service integrations are agreed. The following are open engineering/product choices, with the milestone by which they must be resolved:

| Decision | Proposed starting position | Resolve by |
| --- | --- | --- |
| Conflict granularity and compound operations | Block/field scope when compatible; explicit transactions for structural changes; validate before accepting document-level replacement. | M0 |
| Timestamp authority, skew handling, and tie-breaks | Use recorded edit timestamps with a defined clock policy and stable secondary keys; retain base/dependency metadata for conflict detection. | M0 |
| History retention, offline horizon, and journal placement | Durable recoverable versions and device queues outside rebuildable indexes; coordinate retention with stale-device resync. | M0 |
| Native platform/release matrix | Android and iOS sources and the initial baseline are selected in [upstream-baseline.md](./upstream-baseline.md); HarmonyOS is out of scope. Confirm desktop OS targets, minimum OS versions, signing/distribution and supported client versions. | M0 |
| Vendor-service replacement map | Remove inherited integrations; explicitly choose replacements or retire affected capabilities, preserving local content and documenting cloud-only data migration. | M0 inventory, M1–M2 service work, M6 client cleanup |
| First identity provider and deployment stack | External identity/control plane; choose the smallest stack that covers human and agent access without rewriting the kernel. | M1 |
| Account membership in multiple orgs | Independent memberships and caches; no multi-workspace org model. Confirm how much org-switching UX is needed for the pilot. | M1 |
| Hosted capabilities and offline exceptions | Inventory plugins/snippets, raw routes, imports/restores, and complex offline operations; explicitly approve any exclusions. | M2 / before M5 implementation |
| Agent credential/delegation policy | Named workspace agents and attributable delegated tokens with revocation and bounded privileges. | M2 |
| Sync protocol and UI integration | Extend existing transaction/transport boundaries; no assumption that replacing files or broadcasting alone suffices. | M0 prototype, finalized before M4 |
| Pilot size, latency, recovery, and resource budgets | Start with the proposed benchmark and define representative documents/databases/assets, RPO/RTO, and offline backlogs. | M0 targets, validated in M7 |

The next implementation step is **M0**, beginning with mutation/permission inventories and a small offline conflict/recovery prototype. Scope changes discovered there must be recorded explicitly; do not quietly downgrade v0 to a web-only or online-only product.
