import re


class WeakPassword(Exception):
    pass


def check_password_complexity(password) -> None:
    """Password complexity check.

    Primary conditions for password validation :

    Minimum 8 characters.
    The alphabets must be between [a-z]
    At least one alphabet should be of Upper Case [A-Z]
    At least 1 number or digit between [0-9].
    At least 1 character from [ _ or @ or $ ].
    """

    if len(password) < 8:
        raise WeakPassword

    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"

    # compiling regex
    pat = re.compile(reg)

    # searching regex
    mat = re.search(pat, password)

    # validating conditions
    if not mat:
        raise WeakPassword
