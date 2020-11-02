#!/usr/bin/env python3
"Creates a firefox "

import argparse
import sys
import os.path as pt

def main():
    "Main Function"
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL for the webapp")
    parser.add_argument(
        "-n", "--name",
        help=("Name of the app as shown in the menu. In absence of this, the "
              "title of page will be used.")
    )

    parser.add_argument(
        "-e", "--exec-name",
        help="Name of the script that will be created in binary directory."
    )

    parser.add_argument(
        "-l", "--logo",
        help="URL/path for the logo. If omitted, the favicon will be used."
    )

    parser.add_argument(
        "-f", "--firefox-profile",
        help="Firefox Profile path. If omitted, the default profile is used"
    )
    args = parser.parse_args()

    # Add Missing Arguments with default values
    if args.firefox_profile is None:
        profile_path = pt.dirname(sys.argv[0]) + "/.firefox_profile"
        with open(profile_path) as prof:
            args.firefox_profile = prof.readline()[:-1]
    print(args)


if __name__ == "__main__":
    main()
