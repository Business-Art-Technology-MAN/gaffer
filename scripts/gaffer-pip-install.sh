#!/usr/bin/env bash
# Install Python packages using Gaffer's embedded Python.
# Packages go to ~/gaffer/python_packages (on PYTHONPATH when using this repo's _gaffer.py).
#
# Finds a built install (bin/__private/gaffer or .exe), in order:
#   1. GAFFER_ROOT if set (install root or .../bin)
#   2. GAFFER_BUILD_DIR (SCons output: directory that contains bin/)
#   3. Walk up from $PWD
#   4. Walk up from this script's repo root

set -euo pipefail

_engine_in_tree() {
	local root="$1"
	[[ -f "${root}/bin/__private/gaffer.exe" ]] || [[ -x "${root}/bin/__private/gaffer" ]]
}

_try_set_root_from() {
	local r="${1:-}"
	[[ -n "$r" ]] || return 1
	if _engine_in_tree "$r" ; then
		GAFFER_ROOT="$r"
		return 0
	fi
	if [[ -f "${r}/__private/gaffer.exe" ]] || [[ -x "${r}/__private/gaffer" ]] ; then
		GAFFER_ROOT="$(cd "${r}/.." && pwd)"
		return 0
	fi
	return 1
}

_climb_from() {
	local d="$1"
	local prev=""
	while [[ -n "$d" ]] ; do
		if _try_set_root_from "$d" ; then
			return 0
		fi
		prev="$d"
		d="$(cd "${d}/.." && pwd)"
		[[ "$d" != "$prev" ]] || return 1
	done
	return 1
}

if [[ -n "${GAFFER_ROOT:-}" ]] ; then
	_user="${GAFFER_ROOT}"
	if ! _try_set_root_from "${_user}" ; then
		echo "ERROR: GAFFER_ROOT was \"${_user}\" but no bin/__private/gaffer (or .exe) found there." >&2
		exit 1
	fi
elif [[ -n "${GAFFER_BUILD_DIR:-}" ]] && _try_set_root_from "${GAFFER_BUILD_DIR}" ; then
	:
elif _climb_from "${PWD}" ; then
	:
else
	_repo="$(cd "$(dirname "$0")/.." && pwd)"
	if ! _climb_from "${_repo}" ; then
		echo "ERROR: No bin/__private/gaffer (or .exe) found. Build Gaffer, then set GAFFER_BUILD_DIR or GAFFER_ROOT, or cd to your install and retry." >&2
		exit 1
	fi
fi

GAFFER_BIN="${GAFFER_ROOT}/bin/gaffer"
if [[ ! -x "$GAFFER_BIN" ]] ; then
	echo "ERROR: ${GAFFER_BIN} not found or not executable." >&2
	exit 1
fi

PIP_TARGET="${HOME}/gaffer/python_packages"
mkdir -p "${PIP_TARGET}"

echo "Using GAFFER_ROOT=${GAFFER_ROOT}"
echo "pip install --target ${PIP_TARGET}"
exec "${GAFFER_BIN}" env python -m pip install "$@" --target "${PIP_TARGET}"
