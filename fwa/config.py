from pathlib import Path
import shutil

import toml


class _Config:
    DIR = Path.home() / ".config" / "fwa"
    FILE = DIR / "config.toml"
    ICON_DIR = DIR / "icons"
    BIN_DIR = Path.home() / ".local" / "bin"

    def __init__(self):
        for directory in (self.DIR, self.ICON_DIR, self.BIN_DIR):
            if not directory.exists():
                directory.mkdir(parents=True)

        if not self.FILE.exists():
            self.FILE.touch()

        with open(self.FILE) as f:
            self.conf = toml.load(f)

    def write_config(self):
        with open(self.FILE, "w") as f:
            toml.dump(self.conf, f)


Config = _Config()


def _get_firefox_bin() -> str:
    """
    Returns a firefox binary name that exists in PATH
    """
    for name in (
        "firefox",
        "firefox-developer-edition",
        "firefox-esr",
        "firefox-nightly",
        "firefox-beta",
        "firefox-trunk",
    ):
        if shutil.which(name):
            return name
    raise OSError("Firefox binary not found in $PATH")


FIREFOX_BINARY = _get_firefox_bin()
