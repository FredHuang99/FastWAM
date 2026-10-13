#!/usr/bin/env bash
set -euo pipefail
export FW_BRIDGE_MACHINE=h100
exec bash "$(dirname "${BASH_SOURCE[0]}")/../grasp_launch.sh" "$@"
