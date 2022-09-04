# Script for issue badge to a user
import requests
import json
from datetime import datetime
from app import Settings
from app.db import Assertions


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


def wrangle_assertion(
    assertion: dict,
    badge_name: str,
):
    # Convert all the fields to strings using dict comprehension
    fields = {
        k: str(v)
        for k, v in assertion.items()
        if k not in ["recipient_hashed", "revoked"]
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

    # Convert to date time
    for k, v in fields.items():
        try:
            if type(v) == str:
                fields[k] = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            # Try different format
            try:
                fields[k] = datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                print("Could not convert to date time: " + str(v))
                pass

    # Convert createdAt to a datetime object from ISO8601
    ca = fields["issuedOn"]

    # Get the badge name that the assertion is for by querying the badges table
    orgname = "Bioinformatics Research Network"

    # Build linkedin url
    linkedin_share_url = (
        "https://www.linkedin.com/profile/add?startTask=CERTIFICATION_NAME"
        + f"&name={badge_name}&organizationName={orgname}&issueYear={ca.year}"
        + f"&issueMonth={ca.month}"
        + f'&certUrl={fields["openBadgeId"]}'
        + f'&certId={fields["entityId"]}'
    )
    # If credential expires, add the expiration date to the share URL
    if fields["expires"] != "None":
        exp = fields["expires"]
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
        + f' src="{fields["openBadgeId"]}?embedVersion=1&amp;'
        + f'embedWidth=330&amp;embedHeight=191{ident_card}" '
        + f'title="Badge: {badge_name}" style="width: 330px; height: 191px;'
        ' border: 0px;"></iframe>'
    )
    fields["embed_card_html"] = embed_card_html

    # Create embed badge html
    award_date = ca.strftime("%B %d, %Y")
    embed_badge_html = (
        '<blockquote class="badgr-badge" style="font-family: Helvetica, Roboto,'
        + ' &quot;Segoe UI&quot;, Calibri, sans-serif;">'
        + f'<a href="{fields["openBadgeId"]}"><img width="120px" height="120px"'
        + f' src="{fields["image"]}"></a>'
        + '<p class="badgr-badge-name" style="hyphens: auto; overflow-wrap:'
        + " break-word; word-wrap: break-word;"
        + " margin: 0; font-size: 16px; font-weight: 600; font-style: normal;"
        + " font-stretch: normal; line-height: 1.25;"
        + " letter-spacing: normal; text-align: left; color:"
        + f' #05012c;">{badge_name}</p><p class="badgr-badge-date" '
        + 'style="margin: 0; font-size: 12px; font-style: normal; font-stretch:'
        + " normal; line-height: 1.67; letter-spacing: "
        + 'normal; text-align: left; color: #555555;"><strong style="font-size:'
        + " 12px; font-weight: bold; font-style: "
        + "normal; font-stretch: normal; line-height: 1.67; letter-spacing:"
        + ' normal; text-align: left; color: #000;">'
        + f'Awarded: </strong>{award_date}</p><p style="margin: 16px 0;'
        + ' padding: 0;"><a class="badgr-badge-verify" target="_blank"'
        + f' href="https://badgecheck.io?url={fields["openBadgeId"]}"'
        + ' style="box-sizing: content-box; display: flex; align-items: '
        + "center; justify-content: center; margin: 0; font-size:14px;"
        + " font-weight: bold; width: 48px; height: 16px; border-radius:"
        + " 4px; border: solid 1px black; text-decoration: none; padding: 6px"
        + ' 16px; margin: 16px 0; color: black;">VERIFY</a></p>'
        + '<script async="async"'
        + ' src="https://badgr.com/assets/widgets.bundle.js"></script></blockquote>'
    )
    fields["embed_badge_html"] = embed_badge_html

    # Filter to only include the fields that are in the Assertions model
    fields = {
        k: v
        for k, v in fields.items()
        if k in Assertions.__table__.columns.keys()
    }

    # Remove fields which have a value of None
    fields = {k: v for k, v in fields.items() if v is not None and v != "None"}

    return fields


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
    # TODO: Have a way to add in custom URL and evidence for the assertion
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
                    "url": "https://bioresnet.org/",
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
