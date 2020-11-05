#!/usr/bin/env bash
# Usage: ./setup.sh

set -euo pipefail

REPO_DIR="$(dirname "$0")"
BIN_DIR="$REPO_DIR/bin"
ICON_DIR="$REPO_DIR/icons"
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
			echo -n "Enter path to existing profile (or run the script with --firefox_profile): "
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

# Check if firefox_profile is valid
if ! [[ -d $FIREFOX_PROFILE ]]; then
	echo "Invalid Firefox Profile Path"
	exit 3
fi

# Store Profile to be used
echo "$FIREFOX_PROFILE" > "$REPO_DIR/.firefox_profile"

echo "Enabling userChrome.css support"
echo -e '\nuser_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);' >> "$FIREFOX_PROFILE/user.js"

# Starting firefox for customizability
firefox --profile "$FIREFOX_PROFILE" "$FIRST_LAUNCH" &

echo ""
echo "Hit Enter once you have completed customizing the profile."
read -r

# userChrome Hacks
#
# Initially stores all selectors to be hidden in HIDDEN_SELECTORS, followed by
# writing a CSS rule that hides them all

mkdir "$FIREFOX_PROFILE/chrome" &> /dev/null || true
HIDDEN_SELECTORS=()
echo -n "Do you want to hide tabs? (y/N) "
read -r input
if [[ ${input^^} == "Y" ]]; then
	HIDDEN_SELECTORS=("${HIDDEN_SELECTORS[@]}" "#tabbrowser-tabs")
fi

echo -n "Do you want to hide main toolbar (address bar, back, forward, etc)? (y/N) "
read -r input
if [[ ${input^^} == "Y" ]]; then
	HIDDEN_SELECTORS=("${HIDDEN_SELECTORS[@]}" "#nav-bar")
fi

function join_by {
	local IFS="$1";
	shift;
	echo -n "$*";
}

if (( ${#HIDDEN_SELECTORS[@]} > 0 )); then
	join_by , "${HIDDEN_SELECTORS[@]}" >> "$FIREFOX_PROFILE/chrome/userChrome.css"
	echo "{
	visibility: collapse !important;
}" >> "$FIREFOX_PROFILE/chrome/userChrome.css"
fi

echo "Optional: Add $(cd "$ICON_DIR"; pwd) to your PATH to allowing launching the app from command line"
