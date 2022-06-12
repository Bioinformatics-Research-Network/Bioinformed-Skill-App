from functools import wraps
from flask import redirect, url_for
from flask_login import current_user


def onboarding_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.onboarded:
            return redirect(url_for("routes.onboarding"))
        return f(*args, **kwargs)

    return decorated_function


def email_verification_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.email_verified:
            return redirect(url_for("routes.email_verification"))
        return f(*args, **kwargs)

    return decorated_function
