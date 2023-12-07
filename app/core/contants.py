from enum import Enum


class UserLoginType(str, Enum):
    EMAIL = "EMAIL"
    GOOGLE = "GOOGLE"


class VisibilityChoices(str, Enum):
    EVERYONE = 'everyone'
    ONLY_AUTHOR = 'only_author'
    FOLLOWERS = 'followers'
