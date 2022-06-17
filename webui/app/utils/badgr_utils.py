# Script for issue badge to a user
import requests
import json
from datetime import datetime
from app.config import Settings
from app.models import Assertions, Badges
from app.db import db_session


def get_bearer_token(config: Settings):
    """
    Get the bearer token from the Badgr API.
    Scope is limited to read-only access for organization-level badges.
    Includes write access for user-level badges.

    :param config: The configuration dictionary for the Badgr API

    :return: The bearer token as a string
    """
    url = config.BADGR_BASE_URL + "/o/token/"
    payload = {
        "username": config.BADGR_USERNAME,
        "password": config.BADGR_PASSWORD,
        "scope": config.BADGR_SCOPE,
        "grant_type": config.BADGR_GRANT_TYPE,
        "client_id": config.BADGR_CLIENT_ID,
    }
    response = requests.request("POST", url, data=payload)
    try:
        token = response.json()["access_token"]
        return token
    except KeyError:  # pragma: no cover
        raise Exception("Badgr API provided no access token.")


def get_assertion(
    assessment_name: str, user_email: str, bearer_token: str, config: Settings
):
    """
    Get the badge assertion from the Badgr API

    :param assessment_name: The assessment name
    :param user_email: The user's email
    :param bearer_token: The bearer token (from the Badgr API)
    :param config: The configuration dictionary for the Badgr API

    :return: The assertion as a response object
    """
    url = (
        config.BADGR_BASE_URL
        + "/v2/badgeclasses/"
        + config.BADGE_IDs[assessment_name]
        + "/assertions"
        + "?recipient="
        + user_email
        + "&num=1"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + bearer_token,
    }

    response = requests.request("GET", url, headers=headers)
    return response


# TODO: Pydantic schema for this?
def issue_badge(
    user_email: str,
    user_first: str,
    user_last: str,
    assessment_name: str,
    bearer_token: str,
    config: Settings,
):
    """
    Issue a badgr badge to a user

    :param user_email: The user's email
    :param user_first: The user's first name
    :param user_last: The user's last name
    :param assessment_name: The assessment name
    :param bearer_token: The bearer token (from the Badgr API)
    :param config: The configuration dictionary for the Badgr API

    :return: The assertion as a response object
    """
    # Get the URL for the badge, based on assessment name
    url = (
        config.BADGR_BASE_URL
        + "/v2/badgeclasses/"
        + config.BADGE_IDs[assessment_name]
        + "/assertions"
    )

    # Prepare the payload with custom text and evidence
    payload = json.dumps(
        {
            "recipient": {
                "identity": user_email,
                "type": "email",
                "hashed": True,
            },
            "narrative": "This award certifies that "
            + user_first
            + " "
            + user_last
            + " has successfully completed the Bioinformatics Research Network "
            + assessment_name
            + " skill assessment.",
            "evidence": [
                {
                    "narrative": (
                        "Link to a place where someone can see the results???"
                    )
                }
            ],
            "notify": True,
        }
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + bearer_token,
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response


def get_all_badges(bearer_token: str, config: Settings):
    """
    Get all badges from the Badgr API

    :param config: The configuration dictionary for the Badgr API

    :return: The response object
    """
    url = (
        config.BADGR_BASE_URL
        + "/v2/issuers/"
        + config.BADGR_ISSUER_ID
        + "/badgeclasses"
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + bearer_token,
    }
    response = requests.request("GET", url, headers=headers)
    response.raise_for_status()
    return response


def get_all_assertions(bearer_token: str, config: Settings):
    """
    Get the badge assertion from the Badgr API

    :param assessment_name: The assessment name
    :param user_email: The user's email
    :param bearer_token: The bearer token (from the Badgr API)
    :param config: The configuration dictionary for the Badgr API

    :return: The assertion as a response object
    """
    url = (
        config.BADGR_BASE_URL
        + "/v2/issuers/"
        + config.BADGR_ISSUER_ID
        + "/assertions"
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + bearer_token,
    }

    response = requests.request("GET", url, headers=headers)
    response.raise_for_status()
    return response


def wrangle_assertion(assertion: dict):
    # Convert all the fields to strings using dict comprehension -- skipping the boolean fields
    fields = {
        k: str(v)
        for k, v in assertion.items()
        if not k in ["recipient_hashed", "revoked"]
    }

    # Wrangle the recipient field
    fields["recipient_identity"] = assertion["recipient"]["identity"]
    fields["recipient_hashed"] = assertion["recipient"]["hashed"]
    fields["recipient_type"] = assertion["recipient"]["type"]
    fields["recipient_plaintextIdentity"] = assertion["recipient"][
        "plaintextIdentity"
    ]
    if "salt" in assertion["recipient"].keys():
        fields["recipient_salt"] = assertion["recipient"]["salt"]

    # Wrangle the evidence field
    if len(assertion["evidence"]) > 0:
        fields["evidence_url"] = assertion["evidence"][0]["url"]
        fields["evidence_narrative"] = assertion["evidence"][0]["narrative"]

    # Convert createdAt to a datetime object from ISO8601
    ca = datetime.strptime(assertion["createdAt"], "%Y-%m-%dT%H:%M:%SZ")

    # Get the badge name that the assertion is for by querying the badges table
    badge_name = (
        db_session.query(Badges)
        .filter_by(entityId=assertion["badgeclass"])
        .first()
        .name
    )
    orgname = "Bioinformatics Research Network"

    # Build linkedin url
    linkedin_share_url = (
        f"https://www.linkedin.com/profile/add?startTask=CERTIFICATION_NAME"
        + f"&name={badge_name}&organizationName={orgname}&issueYear={ca.year}"
        + f"&issueMonth={ca.month}"
        + f'&certUrl={fields["openBadgeId"]}'
        + f'&certId={fields["entityId"]}'
    )
    # If credential expires, add the expiration date to the share URL
    if fields["expires"] != "None":
        exp = datetime.strptime(fields["expires"], "%Y-%m-%dT%H:%M:%SZ")
        linkedin_share_url += (
            f"&expirationYear={exp.year}" + f"&expirationMonth={exp.month}"
        )
    fields["linkedin_add_profile_url"] = linkedin_share_url

    # Add twitter share URL
    tweet_text = (
        f'I earned the "{badge_name}" badge from @BRN_science!'
        + f'%0A%0A{fields["openBadgeId"]}'
    )
    twitter_share_url = (
        f"https://twitter.com/intent/tweet?text={tweet_text}".replace(
            " ", "%20"
        )
        .replace("#", "%23")
        .replace('"', "%22")
    )
    fields["twitter_share_url"] = twitter_share_url

    # Add facebook share URL
    facebook_share_url = (
        f'https://www.facebook.com/sharer/sharer.php?u={fields["openBadgeId"]}'
    )
    fields["facebook_share_url"] = facebook_share_url

    # Share to linkedin feed
    linkedin_share_url = f'https://www.linkedin.com/sharing/share-offsite/?url={fields["openBadgeId"]}'
    fields["linkedin_share_url"] = linkedin_share_url

    # Check for identity email
    ident = ""
    if fields["recipient_type"] == "email":
        ident = fields["recipient_plaintextIdentity"]
        ident_card = "&amp;identity__email=" + ident
        share_url = fields["openBadgeId"] + "?identity__email=" + ident
    else:
        share_url = fields["openBadgeId"]
        ident_card = ""

    # Add share URL
    fields["share_url"] = share_url

    # Add embeded card HTML
    embed_card_html = (
        "<iframe"
        f' src="{fields["openBadgeId"]}?embedVersion=1&amp;embedWidth=330&amp;embedHeight=191{ident_card}" '
        + f'title="Badge: {badge_name}" style="width: 330px; height: 191px;'
        ' border: 0px;"></iframe>'
    )
    fields["embed_card_html"] = embed_card_html

    # Create embed badge html
    award_date = ca.strftime("%B %d, %Y")
    embed_badge_html = (
        f'<blockquote class="badgr-badge" style="font-family: Helvetica,'
        f' Roboto, &quot;Segoe UI&quot;, Calibri, sans-serif;">'
        + f'<a href="{fields["openBadgeId"]}"><img width="120px" height="120px"'
        f' src="{fields["image"]}"></a>'
        + f'<p class="badgr-badge-name" style="hyphens: auto; overflow-wrap:'
        f" break-word; word-wrap: break-word;"
        + f" margin: 0; font-size: 16px; font-weight: 600; font-style: normal;"
        f" font-stretch: normal; line-height: 1.25;"
        + " letter-spacing: normal; text-align: left; color:"
        f' #05012c;">{badge_name}</p><p class="badgr-badge-date" '
        + f'style="margin: 0; font-size: 12px; font-style: normal;'
        f" font-stretch: normal; line-height: 1.67; letter-spacing: "
        + f'normal; text-align: left; color: #555555;"><strong'
        f' style="font-size: 12px; font-weight: bold; font-style: '
        + f"normal; font-stretch: normal; line-height: 1.67; letter-spacing:"
        f' normal; text-align: left; color: #000;">'
        + f'Awarded: </strong>{award_date}</p><p style="margin: 16px 0;'
        ' padding: 0;"><a class="badgr-badge-verify" target="_blank"'
        + f' href="https://badgecheck.io?url={fields["openBadgeId"]}"'
        ' style="box-sizing: content-box; display: flex; align-items: '
        + f"center; justify-content: center; margin: 0; font-size:14px;"
        f" font-weight: bold; width: 48px; height: 16px; border-radius:"
        + f" 4px; border: solid 1px black; text-decoration: none; padding: 6px"
        f' 16px; margin: 16px 0; color: black;">VERIFY</a></p>'
        + f'<script async="async"'
        f' src="https://badgr.com/assets/widgets.bundle.js"></script></blockquote>'
    )
    fields["embed_badge_html"] = embed_badge_html

    # Filter to only include the fields that are in the Assertions model
    fields = {
        k: v
        for k, v in fields.items()
        if k in Assertions.__table__.columns.keys()
    }

    return fields
