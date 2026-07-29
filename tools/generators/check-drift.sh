#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# Fail if any generated artifact has drifted from grammar/grammar.ebnf.
# Thin wrapper over `regen-all.sh --check`, kept as its own entry point because
# that is the name CI and grammar/keywords.yaml both refer to.
set -euo pipefail
exec "$(dirname "$0")/regen-all.sh" --check "$@"
