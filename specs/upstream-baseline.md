# Upstream Baseline and Integration Record

Selected by the project owner on 2026-10-22: **SiYuan 3.8.8**, with the following fixed native sources. This is the starting source baseline for RW Notes v0, not a declaration that v0 is implemented or that all native builds have passed.

## Pinned sources

| Component | Official repository | Reference | Exact upstream commit |
| --- | --- | --- | --- |
| Core, shared frontend, desktop and mobile kernel | `siyuan-note/siyuan` | `v3.8.8` | `bfe36100477b7bbd66db1a8b8cff5547b2ccdb59` |
| Android shell | `siyuan-note/siyuan-android` | `v3.8.8` | `89c50f2deaccabfab7b9fe5f94d172887f45b95f` |
| iOS shell | `siyuan-note/siyuan-ios` | Selected commit; no upstream release tag | `05280f32ba89705e3ba55c233037db02c93cdea8` |

The iOS SHA is an agreed compatibility candidate, **not a verified mapping to the App Store binary**. It predates the 3.8.8 store release and contains the preceding native changes. Its committed marketing version is 3.8.7; RW Notes sets its own app and share-extension marketing versions to 3.8.8. Public upstream records contain no iOS release tag, build artifact, or release-to-SHA attestation. Upstream's [release procedure](https://github.com/siyuan-note/siyuan/blob/v3.8.8/docs/RELEASE-VERIFICATION.zh-CN.md) describes manual iOS builds and direct App Store uploads.

Store observations on 2026-10-22: [Apple App Store](https://apps.apple.com/us/app/siyuan/id1583226508) and [Google Play](https://play.google.com/store/apps/details?id=org.b3log.siyuan) published 3.8.8, updated October 20; [F-Droid](https://f-droid.org/en/packages/org.b3log.siyuan/) listed 3.8.7. Store listings are supporting context, not immutable source provenance.

## Branch and build policy

- Keep core `master` and mobile `main` as upstream tracking branches. They may advance beyond this baseline; fetching them does not change the selected baseline.
- Develop on `rw-notes` in each fork. Integrate only a deliberately selected upstream release/commit combination and update this record in the same change. Do not blindly merge a newer mobile `main` merely because its displayed version matches.
- Keep the three checkouts adjacent: `repos/rw-notes`, `repos/rw-notes-android`, and `repos/rw-notes-ios`. These are separate repositories, not submodules.
- Build both shared frontend resources and mobile kernels from the same RW Notes core commit incorporating the pinned core baseline. Record the **actual fork SHAs**, toolchain versions, and artifact checksums for each build; upstream SHAs alone do not identify the branded binaries.
- Android consumes `app/libs/kernel.aar` and `app/src/main/assets/app.zip`. iOS consumes `../rw-notes/kernel/ios/iosk.xcframework` plus the shared frontend resources copied into its `app/` directory. Do not reuse stale upstream binaries.
- Upstream 3.8.8 is separate from RW Notes v0. The selected version fields do not advertise collaboration, role enforcement, or vendor-service removal as delivered.

## Alignment performed

Recovery branches named `backup/rw-notes-before-3.8.8-20261022` preserve the pre-integration fork heads:

| Fork | Previous `rw-notes` head | Integration approach |
| --- | --- | --- |
| Core | `eccaf20e639c6625218a2b29200d71d2db521450` | Merge the exact 3.8.8 core commit, retaining planning, branding, local entitlement patches and Docker customizations |
| Android | `8591cd0def75c46d250da83cc7bc72a70cfc4606` | Restore the 3.8.8 source configuration in a new commit, retaining RW Notes branding; no published history rewrite |
| iOS | `c16b50faeda77774ed7d4b8d1f4df62934431b3f` | Already based on the selected SHA; retain branding and adjacent kernel path, align marketing version and documentation |

Android history still contains the previously imported 3.8.9 alpha commits, but their source/configuration changes are reversed in the baseline alignment commit. Its effective source base is 3.8.8 plus the recorded fork changes. A later upgrade must explicitly reapply/review the reversed changes; Git ancestry alone will not reintroduce them when merging `main`.

## Compatibility ledger

| Surface | Preserved behavior / integration adjustment |
| --- | --- |
| Branding | Retain source SVG, generated desktop/native assets, RW Notes package IDs, labels, slogan, and English-only top-level README policy |
| Language files | Port branding to upstream's renamed locale files; keep new upstream keys and translations. Regenerate startup-language resources from these sources |
| User guides | Keep the updated 3.8.8 document structures and IDs while retaining fork branding on previously customized pages |
| Startup and packaging | Retain new upstream startup logic, manifests and installer process handling; apply RW Notes display names without renaming kernel executables or protocol/bridge identifiers |
| Docker | Retain upstream OCR/runtime build stages, with `/opt/rw-notes`, `/home/rw-notes`, workspace environment alias and user-home handling; pass the new `serve` subcommand |
| Local entitlement patch | Retain the existing local user response and `IsPaidUser` override through the typed settings API and current configuration accessors. This transitional patch does not implement organization identities or complete vendor-service removal |
| Upstream updater | Retain disabled update API behavior, disabled package-download default, migration of an enabled download setting, and no update check when opening the guide |
| Removed upstream code | Do not resurrect the obsolete account-display configuration, old locale filenames, retired repository settings UI, or obsolete boot PNG output |
| Android build | Restore 3.8.8 Gradle configuration/version code 439 and adapt the fork's variant checks to that configuration; retain app IDs, resources and artifact naming |
| iOS build | Preserve native bridges, app groups and framework path; marketing version 3.8.8 is a fork configuration change |

## Validation and remaining M0 work

Integration checks on 2026-10-22:

- Passed frontend `pnpm run lint` (both TypeScript configurations, ESLint, CSS/menu contracts and generated startup-language consistency), plus 13 desktop workspace/window-message tests.
- Passed translation validation across 22 locale files, including kernel format placeholders; parsed 104 changed JSON/guide/manifest files and both AppX manifests.
- Passed focused Go tests for the typed cached-account API, RW Notes local entitlement response and role boundary, declared settings writes, network-proxy handling, and disabled inherited installer policy. Windows/macOS-only installer scenarios remain platform-skipped on this Linux host; their assertions were adapted to the disabled updater while retaining package-helper coverage.
- Passed Android configuration checks for all eight variants (IDs, labels, artifact names, SDK/ABI and signing-configuration wiring) using a temporary empty signing configuration that was removed afterward. Compiled native resource sources with SDK `aapt2` 36.1.0. The full Gradle resource pipeline stops at missing `app/libs/kernel.aar`; it is not a completed Android build.
- Passed iOS project parsing, project/app marketing version, app/share bundle IDs, framework path, plist/entitlement and asset-catalog checks. No Xcode build was performed on this Linux host.
- Passed shell/JavaScript syntax checks and a mocked Docker entrypoint check covering `serve`, argument forwarding and CLI/RW Notes/upstream workspace-variable precedence. No container image build or running service restart was performed.
- Verified the source SVG and generated branding assets were preserved, the fork delta was retained/adapted at moved paths, and no merge conflicts or whitespace errors remain in the fork delta.

The local entitlement patch now lives in `kernel/model/rw_notes_user.go` and uses the upstream account mutex; the API adapter retains read-only cached requests. This is integration maintenance of existing fork behavior, not a new user-management design.

Full desktop/Docker/native packaging and device verification remain required before calling this a verified working baseline. In particular, build Android and iOS with the matching core frontend/kernel, launch on devices, create/edit/reopen a local workspace, and exercise import/export, assets, database views, sharing, and suspend/resume. These checks establish baseline compatibility, not the future collaboration protocol.

Re-run the architecture, API/MCP, identity, mutation and vendor-service inventories against 3.8.8: the earlier planning assessment was made on 3.5.8. Upstream now includes additional API contracts, MCP/agent facilities, configuration snapshots and encrypted-notebook functionality. Preserve existing encrypted-data recovery paths when designing collaboration; do not assume the old inventory is exhaustive.
