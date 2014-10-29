def error(code, msg):
    return dict(what="error", code=code, msg=msg)


LOGIN_FAIL = error(1, "Login or Password incorrect")
WALKING_TOO_FAR = error(2, "Walking too far")
UNKNOWN_TARGET = error(3, "Unknown target")

