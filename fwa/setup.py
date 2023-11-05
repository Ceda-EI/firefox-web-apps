from pathlib import Path
import subprocess
from typing import Annotated, Optional

from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
import typer

from fwa.config import FIREFOX_BINARY, Config
from fwa.log import err, out
from fwa.validation import BoolStrValidator, ProfilePathValidator, str_to_bool


DEFAULT_PROFILE_NAME = "firefox-web-apps"


def bool_prompt(message: str, default: Optional[bool] = None) -> bool:
    return str_to_bool(
        prompt(
            message,
            validator=BoolStrValidator(default=default),
        ),
        default=default,
    )


def enable_user_chrome(profile: Path):
    with open(profile / "user.js", "a") as f:
        f.write("\n")
        f.write(
            'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);'
        )
        f.write("\n")


def configure_user_chrome(
    profile: Path, hide_tabs: bool, hide_main_toolbar: bool, disable_url_bar: bool
):
    chrome_dir = profile / "chrome"

    if not chrome_dir.exists():
        chrome_dir.mkdir()

    v_collapse = []
    if hide_tabs:
        v_collapse.append("#tabbrowser-tabs")
        v_collapse.append("#TabsToolbar")

    if hide_main_toolbar:
        v_collapse.append("#nav-bar")


    with open(chrome_dir / "userChrome.css", "a") as f:
        if v_collapse:
            f.write(", ".join(v_collapse))
            f.write("{ visibility: collapse !important; }\n")

        if disable_url_bar:
            f.write(".urlbarView { display: none !important; }\n")
            f.write(".urlbar-input-box { visibility: hidden !important; }\n")


def setup(
    firefox_profile: Annotated[
        Optional[Path],
        typer.Option(
            "-f", "--firefox-profile", help="Path to existing firefox profile"
        ),
    ] = None,
    new_profile_name: Annotated[
        Optional[str],
        typer.Option("-n", "--new-profile", help="Name for a new firefox profile"),
    ] = None,
):
    """
    This program will optionally create a firefox profile and configure it to
    use with Firefox Web Apps
    """
    if firefox_profile is None:
        if new_profile_name is None:
            # prompt for new profile name
            use_existing = bool_prompt(
                "Use an existing profile for apps? (y/N):", False
            )
            if use_existing:
                firefox_profile = Path(
                    prompt(
                        "Enter path to existing profile: ",
                        validator=ProfilePathValidator,
                        completer=PathCompleter(),
                        complete_while_typing=True,
                    )
                )
            else:
                new_profile_name = DEFAULT_PROFILE_NAME

        if new_profile_name:
            firefox_profile = Path.home() / ".mozilla" / "firefox" / new_profile_name
            if firefox_profile.exists():
                err.print(
                    f"[red bold]Firefox Profile {str(firefox_profile)!r} already exists"
                )
                raise typer.Exit(code=1)

            out.print("[green]Creating Firefox Profile.")
            subprocess.run(
                [
                    FIREFOX_BINARY,
                    "-CreateProfile",
                    f"{new_profile_name} {firefox_profile}",
                ]
            )
            out.print("[green]Created Firefox Profile")

    else:
        if not firefox_profile.exists():
            err.print(f"[red bold]{str(firefox_profile)!r} does not exist")
            raise typer.Exit(code=1)

        if not firefox_profile.is_dir():
            err.print(f"[red bold]{str(firefox_profile)!r} is not a directory")
            raise typer.Exit(code=1)

    out.print("[green]Writing config...\n")
    Config.conf["firefox-profile"] = str(firefox_profile)
    Config.write_config()

    out.print("[green]Enabling userChrome.css support...\n")
    enable_user_chrome(firefox_profile)

    out.print("[green]Configuring userChrome.css...\n")

    hide_tabs = bool_prompt("Do you want to hide tabs? (Y/n)", True)
    if hide_main_toolbar := bool_prompt("Do you want to hide main toolbar? (y/N)", False):
        hide_url_bar = False
    else:
        hide_url_bar = bool_prompt("Do you want to disable the URL bar? (Y/n)", True)

    configure_user_chrome(
        firefox_profile,
        hide_tabs,
        hide_main_toolbar,
        hide_url_bar,
    )


def main():
    typer.run(setup)
