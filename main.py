## Create a flask app with GitHub OAuth
from app.crud.crud import get_assessments
from flask import Flask, redirect, render_template, url_for, request
from flask_dance.contrib.github import github
from flask_login import logout_user, login_required

from app import config, models, auth, db

app = Flask(__name__)
app.secret_key = config.FLASK_APP_SECRET_KEY  # Replace this with your own secret!
app.register_blueprint(auth.oauth.github_blueprint, url_prefix="/login")
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

models.db.init_app(app)
models.login_manager.init_app(app)

with app.app_context():
    models.db.create_all()
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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@app.route("/assessments")
@login_required
def assessments():
    # Get query parameters
    query_params = {
        "types": request.args.get("types"),
        "languages": request.args.get("languages"),
    }
    assessments = get_assessments(
        db=models.db.session,
        language=query_params["languages"],
        types=query_params["types"],
    )
    languages=["All", 'R', "Python", "Bash", "Nextflow", "Snakemake"]
    types=["All", 'software', "analysis"]
    # Put language first if it is in the query parameters
    if query_params["languages"] in languages:
        languages.remove(query_params["languages"])
        languages.insert(0, query_params["languages"])
    print(assessments)
    return render_template(
        "assessments.html", assessments=assessments,
        languages=languages, types=types
    )


@app.route("/documentation")
@login_required
def documentation():
    return redirect(
        "https://brnteam.notion.site/BRN-Skill-Assessments-09882a8300e64d33925593584afb0fab"
    )
