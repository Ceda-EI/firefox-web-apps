#!/usr/bin/env bash
# Usage: ./setup.sh

set -euo pipefail

REPO_DIR="$(dirname "$0")"
BIN_DIR="$REPO_DIR/bin"
ICON_DIR="$REPO_DIR/icon"
FIRST_LAUNCH="https://gitlab.com/ceda_ei/firefox-web-apps/-/wikis/Getting-Started"
HELP_TEXT="
Usage:
 $0 [-f|--firefox-profile] <firefox_profile> [-n|--new] <profile_name> [-h|--help]

Configure a firefox profile for web apps.

Options:
 -f, --firefox-profile         Path to an existing firefox profile (unless -n is
     <firefox_profile>         also provided)
 -n, --new <profile_name>      Creates a new profile with the given name. -f
                               configures the new profile path when passed along
                               with -n
 -h, --help                    This help page
"

[[ -d $BIN_DIR ]] || mkdir -- "$BIN_DIR"
[[ -d $ICON_DIR ]] || mkdir -- "$ICON_DIR"

FIREFOX_PROFILE=""
PROFILE_NAME="firefox-web-apps"
NEW=0
OPTIONS=f:n:h
LONGOPTS=firefox-profile:,new:,help
PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")
eval set -- "$PARSED"

while true; do
	case "$1" in
		-f|--firefox-profile)
			shift
			FIREFOX_PROFILE="$1"
			shift
			;;
		-n|--new)
			NEW=1
			shift
			PROFILE_NAME="$1"
			shift
			;;
		-h|--help)
			echo "$HELP_TEXT"
			exit
			;;
		--)
			break
			;;
		*)
			echo "Error parsing arguments!"
			exit 1
	esac
done

# Check if firefox is running
if pidof firefox &> /dev/null; then
	echo "It is recommended to close firefox before running this script."
	echo -n "Do you want to run the script anyways? (y/N): "
	read -r input
	if [[ ${input^^} != "Y" ]]; then
		exit 2
	fi
fi

# Prompt to create Firefox profile
if [[ $FIREFOX_PROFILE == "" ]] || (( NEW == 1 )); then
	if (( NEW == 0 )); then
		echo -n "Use an existing profile for apps? (y/N): "
		read -r input
		if [[ ${input^^} == "Y" ]]; then
			echo "Enter path to existing profile (or run the script with --firefox_profile): "
			read -r FIREFOX_PROFILE
		else
			NEW=1
		fi
	fi
	if (( NEW == 1 )); then
		FIREFOX_PROFILE="${FIREFOX_PROFILE:-$HOME/.mozilla/firefox/${PROFILE_NAME}}"
		firefox -CreateProfile "${PROFILE_NAME} ${FIREFOX_PROFILE}"
	fi
fi
