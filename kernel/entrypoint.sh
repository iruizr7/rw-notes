#!/bin/sh
set -e

# Default values
PUID=${PUID:-1000}
PGID=${PGID:-1000}
USER_NAME=${USER_NAME:-rw-notes}
GROUP_NAME=${GROUP_NAME:-rw-notes}
WORKSPACE_DIR="/rw-notes/workspace"

# Get or create group
group_name="${GROUP_NAME}"
if getent group "${PGID}" > /dev/null 2>&1; then
    group_name=$(getent group "${PGID}" | cut -d: -f1)
    echo "Using existing group: ${group_name} (${PGID})"
else
    echo "Creating group ${group_name} (${PGID})"
    addgroup --gid "${PGID}" "${group_name}"
fi

# Get or create user
user_name="${USER_NAME}"
if getent passwd "${PUID}" > /dev/null 2>&1; then
    user_name=$(getent passwd "${PUID}" | cut -d: -f1)
    echo "Using existing user ${user_name} (PUID: ${PUID}, PGID: ${PGID})"
else
    echo "Creating user ${user_name} (PUID: ${PUID}, PGID: ${PGID})"
    adduser --uid "${PUID}" --ingroup "${group_name}" --disabled-password --gecos "" "${user_name}"
fi
user_home=$(getent passwd "${PUID}" | cut -d: -f6)

# Parse command line arguments for --workspace option or workspace path env variables
# Store other arguments in ARGS for later use
if [ -n "${RW_NOTES_WORKSPACE_PATH}" ]; then
    WORKSPACE_DIR="${RW_NOTES_WORKSPACE_PATH}"
elif [ -n "${SIYUAN_WORKSPACE_PATH}" ]; then
    WORKSPACE_DIR="${SIYUAN_WORKSPACE_PATH}"
fi
ARGS=""
while [ "$#" -gt 0 ]; do
    case $1 in
        --workspace=*) WORKSPACE_DIR="${1#*=}"; shift ;;
        *) ARGS="$ARGS $1"; shift ;;
    esac
done

mkdir -p /opt/rw-notes "${user_home}" "${WORKSPACE_DIR}"

# Change ownership of relevant directories, including the workspace directory
echo "Adjusting ownership of /opt/rw-notes, ${user_home}, and ${WORKSPACE_DIR}"
chown -R "${PUID}:${PGID}" /opt/rw-notes
chown -R "${PUID}:${PGID}" "${user_home}"
chown -R "${PUID}:${PGID}" "${WORKSPACE_DIR}"

# Switch to the newly created user and start the main process with all arguments
echo "Starting RW Notes with UID:${PUID} and GID:${PGID} in workspace ${WORKSPACE_DIR}"
exec su-exec "${PUID}:${PGID}" /opt/rw-notes/kernel --workspace="${WORKSPACE_DIR}" ${ARGS}
