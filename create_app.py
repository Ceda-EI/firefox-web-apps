#!/usr/bin/env python3
"Creates a firefox web app"

import argparse
import sys
import os.path as pt
from urllib.parse import urlparse, urlunparse
from collections import Counter

import requests
from bs4 import BeautifulSoup


REPO_DIR = pt.dirname(sys.argv[0])
BIN_DIR = f"{REPO_DIR}/bin"
ICON_DIR = f"{REPO_DIR}/icons"


def eprint(*args, **kwargs):
    "Print an error"
    print(*args, **kwargs, file=sys.stderr)


def url_exists(url):
    "Tests if the url exists after all redirects"
    return requests.head(url, allow_redirects=True).status_code == 200


def absolute_url(base_url, relative_url):
    "Returns the absolute_url if the relative_url is relative"
    base = urlparse(base_url)
    relative = urlparse(relative_url)

    # Make the url absolute if it is not
    if not relative.hostname:
        return urlunparse((*base[:2], *relative[2:]))
    return relative_url


def extract_metadata(url):
    "Extract metadata using bs4"
    # Get and parse the page
    content = requests.get(url, allow_redirects=True).content
    soup = BeautifulSoup(content, 'html.parser')
    metadata = {}

    # Find the title
    titles = [soup.title.string]
    for tag in soup.find_all("meta"):
        title_props = ["title", "og:title", "twitter:title"]
        if tag.get("property", None) in title_props \
           or tag.get("name", None) in title_props:
            titles.append(tag["content"])
    # Set title to the most common if it occurs more than once, else prefer
    # title tag
    most_common = Counter(titles).most_common(1)[0]
    if most_common[1] > 1:
        metadata["title"] = most_common[0].strip()
    else:
        metadata["title"] = soup.title.string.strip()

    # Find the image.
    # Try link first, followed by /favicon.{png,ico}, followed by og:, twitter:
    image = None
    for favicon in soup.find_all("link", rel="icon"):
        if url_exists(absolute_url(url, favicon["href"])):
            image = absolute_url(url, favicon["href"])

    if not image:
        for favicon in [absolute_url(url, i) for i in ("favicon.png", "favicon.ico")]:
            if requests.head(favicon, allow_redirects=True).status_code == 200:
                image = favicon
                break

    if not image:
        for prop in ["og:image", "twitter:image"]:
            prop_tag = soup.find("meta", property=prop)
            if prop_tag and url_exists(absolute_url(url, prop_tag["content"])):
                image = absolute_url(url, prop_tag["content"])
                break

    metadata["image"] = image
    return metadata


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
        profile_path = REPO_DIR + "/.firefox_profile"
        with open(profile_path) as prof:
            args.firefox_profile = prof.readline()[:-1]

    parsed_url = urlparse(args.url)
    if not parsed_url.scheme:
        eprint("Missing URL scheme")
        eprint(f"Maybe you meant https://{args.url} ?")
        sys.exit(1)

    metadata = extract_metadata(args.url)
    if not args.name:
        args.name = metadata["title"]
    if not args.logo:
        args.logo = metadata["image"]
    if not args.exec_name:
        args.exec_name = parsed_url.hostname.replace(".", "-") + "-webapp"

    if "/" in args.exec_name:
        eprint("Executable name can't contain slashes.")
        sys.exit(2)

    if pt.exists(f"{BIN_DIR}/{args.exec_name}"):
        index = 0
        while True:
            if not pt.exists(f"{BIN_DIR}/{args.exec_name}-{index}"):
                args.exec_name = f"{args.exec_name}-{index}"
                break
            index += 1
    print()
    print(f"WebApp Name:\t\t{args.name}")
    print(f"WebApp URL:\t\t{args.url}")
    print(f"Logo URL:\t\t{args.logo}")
    print(f"Executable Name:\t{args.exec_name}")
    print(f"Firefox Profile:\t{args.firefox_profile}")


if __name__ == "__main__":
    main()
