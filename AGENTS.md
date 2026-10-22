# RW-Notes Agents entrypoint
This is a fork from Siyuan note taking software, which includes some improvements/fixes/new functionalities.

The repo is prepared to maintain the `master` branch aligned and synced with the upstream siyuan repo, and the `rw-notes` as a the main branch of the project with periodic merges from the `master`.

In this way, we can benefit from the updates from the main project while developing our changes.

## Our changes
Our changes are described in the `specs/` folder, in several files, each describing a related set of changes. Please maintain them updated, and suggest to create a new file if some requested changes seem to deserve their own spec file.

## Project language
This forks primary development language and user facing locale will be english, but upstream is chineese. So please, take it into account when searching for references of things; they may be in chineese.
## Selected upstream baseline

Follow `specs/upstream-baseline.md`: core/Android 3.8.8 and the pinned iOS commit. Tracking branches may be newer; integrate only deliberate baseline updates. Keep the fork policy in this file when resolving upstream AGENTS changes. Preserve the user-authorized fork customizations while adopting upstream structural changes.
