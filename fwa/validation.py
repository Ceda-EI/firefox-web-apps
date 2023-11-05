from pathlib import Path
from prompt_toolkit.validation import ValidationError, Validator


def str_to_bool(string, default=None):
    normalized = string.lower().strip()
    if normalized in ("yes", "y"):
        return True
    if normalized in ("no", "n"):
        return False
    if default is not None and normalized == "":
        return default
    raise ValueError("could not convert string to bool: {string!r}")


class BoolStrValidator(Validator):
    def __init__(self, default=None):
        self.default = default

    def validate(self, document):
        try:
            str_to_bool(document.text, self.default)
            return True
        except ValueError:
            raise ValidationError(
                cursor_position=0, message="Invalid value. Please enter y/n"
            )


def _is_existing_dir(path):
    return Path(path).is_dir()


ProfilePathValidator = Validator.from_callable(
    _is_existing_dir,
    error_message="Directory does not exist",
)
