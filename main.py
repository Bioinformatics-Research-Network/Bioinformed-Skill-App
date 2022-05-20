## Create a flask app with GitHub OAuth
from app import crud, auth
from datetime import datetime, timedelta
import secrets
from flask import Flask, redirect, render_template, url_for, request, flash
from flask_dance.contrib.github import github
from flask_login import logout_user, login_required, current_user

from app import config, models, auth, db, utils

app = Flask(__name__)
app.secret_key = config.FLASK_APP_SECRET_KEY  # Replace this with your own secret!
app.register_blueprint(auth.oauth.github_blueprint, url_prefix="/login")
app.config["SQLALCHEMY_DATABASE_URI"] = db.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

models.db.init_app(app)
models.login_manager.init_app(app)

with app.app_context():
    models.db.create_all()
    # Fill assessments table from local csv file
    db.fill_db.create_database(
        models.db.session,
    )


@app.route("/")
def homepage():
    if not github.authorized:
        return render_template("index.html")
    else:
        return redirect(url_for("profile"))


@app.route("/github")
def login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    else:
        return redirect(url_for("profile"))


@app.route("/onboarding", methods=["GET"])
@login_required
def onboarding():
    if current_user.onboarded:
        return redirect(url_for("profile"))
    else:
        return render_template("onboarding.html", privacy_url=config.PRIVACY_POLICY_URL)


@app.route("/onboarding", methods=["POST"])
@login_required
def onboarding_submit():
    request_data = request.form
    user = crud.update_user_info(
        models.db.session,
        update_data=request_data,
        user=current_user,
    )
    user.onboarded = True
    models.db.session.commit()
    return redirect(url_for("email_verification"))


@app.route("/email-verification", methods=["GET"])
@login_required
@auth.onboarding_required
def email_verification():
    if current_user.email_verified:
        return redirect(url_for("profile"))
    else:
        # Check for previous verification code
        if current_user.email_verification_code:
            # Check if code is expired
            if current_user.email_verification_code_expiry > datetime.now():
                return render_template(
                    "verify_code_from_email.html", email=current_user.email
                )
        utils.send_verification_email(db=models.db.session, user=current_user)
        return render_template("verify_code_from_email.html", email=current_user.email)


@app.route("/email-verification/resend", methods=["POST"])
@login_required
@auth.onboarding_required
def resend_email_verification():
    utils.send_verification_email(db=models.db.session, user=current_user)
    flash("A new verification code has been sent to " + current_user.email, "info")
    return redirect(url_for("email_verification"))


@app.route("/email-verification", methods=["POST"])
@login_required
@auth.onboarding_required
def email_verification_submit():
    code = request.form["verification_code"]
    if code == current_user.email_verification_code:
        current_user.email_verified = True
        models.db.session.commit()
        utils.send_welcome_email(user=current_user)
        flash("Email verified!", "success")
        return redirect(url_for("profile"))
    else:
        flash("Invalid code", "danger")
        return redirect(url_for("email_verification"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("homepage"))


@app.route("/profile")
@login_required
@auth.onboarding_required
@auth.email_verification_required
def profile():
    return render_template("profile.html")


@app.route("/profile/edit", methods=["POST"])
@login_required
@auth.onboarding_required
@auth.email_verification_required
def edit_profile():
    request_data = request.form
    print(request_data)
    user = crud.update_user_info(
        models.db.session,
        update_data=request_data,
        user=current_user,
    )
    models.db.session.commit()
    flash("Profile updated!", "success")
    return redirect(url_for("profile"))


@app.route("/profile/delete", methods=["POST"])
@login_required
@auth.onboarding_required
@auth.email_verification_required
def delete_profile():
    user = crud.get_user_by_gh_username(
        models.db.session,
        username=current_user.username,
    )
    uname = user.username
    logout_user()
    crud.delete_user(models.db.session, user)
    flash("Your account has been deleted.", "success")
    return redirect(url_for("homepage"))


@app.route("/assessments")
@login_required
@auth.onboarding_required
@auth.email_verification_required
def assessments():
    # Get query parameters
    query_params = {
        "types": request.args.get("types"),
        "languages": request.args.get("languages"),
    }
    assessments = crud.get_assessments(
        db=models.db.session,
        language=query_params["languages"],
        types=query_params["types"],
    )
    languages = ["All", "R", "Python", "Bash", "Nextflow", "Snakemake"]
    types = ["All", "software", "analysis"]
    # Put language first if it is in the query parameters
    if query_params["languages"] in languages:
        languages.remove(query_params["languages"])
        languages.insert(0, query_params["languages"])
    return render_template(
        "assessments.html", assessments=assessments, languages=languages, types=types
    )


@app.route("/documentation")
@login_required
@auth.onboarding_required
@auth.email_verification_required
def documentation():
    return redirect(
        "https://brnteam.notion.site/BRN-Skill-Assessments-09882a8300e64d33925593584afb0fab"
    )


@app.route("/settings")
@login_required
@auth.onboarding_required
@auth.email_verification_required
def settings():
    return render_template("settings.html")
