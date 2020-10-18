#!/usr/bin/env bash
# Usage: ./setup.sh

set -euo pipefail

if pidof firefox &> /dev/null; then
	echo "It is recommended to close firefox before running this script."
	echo -n "Do you want to run the script anyways? (y/N): "
	read -r input
	if [[ ${input^^} != "Y" ]]; then
		exit 2
	fi
fi



REPO_DIR="$(dirname "$0")"
BIN_DIR="$REPO_DIR/bin"
ICON_DIR="$REPO_DIR/icon"

[[ -d $BIN_DIR ]] || mkdir -- "$BIN_DIR"
[[ -d $ICON_DIR ]] || mkdir -- "$ICON_DIR"

FIREFOX_PROFILE=""
OPTIONS=f
LONGOPTS=firefox-profile
PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")
eval set -- "$PARSED"

while true; do
	case "$1" in
		-f|--firefox-profile)
			shift
			FIREFOX_PROFILE="$1"
			;;

		--)
			break
			;;
		*)
			echo "Error parsing arguments!"
			exit 1
	esac
done


# Prompt to create Firefox profile
if [[ $FIREFOX_PROFILE == "" ]]; then
	echo -n "Use an existing profile for apps? (y/N): "
	read -r input
	if [[ ${input^^} == "Y" ]]; then
		echo "Enter path to existing profile (or run the script with --firefox_profile): "
		read -r FIREFOX_PROFILE
	else
		FIREFOX_PROFILE="$HOME/.mozilla/firefox/firefox-web-apps"
		firefox -CreateProfile "firefox-web-apps ${FIREFOX_PROFILE}"
	fi
fi
