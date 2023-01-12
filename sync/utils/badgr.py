# Script for issue badge to a user
import requests
from datetime import datetime
from config import Settings
from models import Badges, Assertions
from sqlalchemy.orm import Session


def badgr_bearer_token(config: Settings):
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


def wrangle_assertion(assertion: dict, db_session: Session):
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
        try:
            fields["evidence_url"] = assertion["evidence"][0]["url"]
        except KeyError:
            fields["evidence_url"] = "None"
        fields["evidence_narrative"] = assertion["evidence"][0]["narrative"]

    # Convert createdAt to a datetime object from ISO8601
    try:
        ca = datetime.strptime(assertion["createdAt"], "%Y-%m-%dT%H:%M:%SZ")
    except KeyError:
        # Add fake timestamp for assertions that don't have a createdAt field
        fields["createdAt"] = "2000-01-01T00:00:00Z"
        ca = datetime.strptime(fields["createdAt"], "%Y-%m-%dT%H:%M:%SZ")
    

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


# Write a function that syncs the badges table with the badgr API
def sync_badges(settings: Settings, db_session: Session):
    # Get all badges from the badgr API
    bt = badgr_bearer_token(settings)
    try:
        badges = get_all_badges(bt, settings)
        badgelst = badges.json()["result"]
    except Exception as e:
        print(str(e))
        raise e

    # Loop through all badges and add them to the badges table
    try:
        for badge in badgelst:
            print(badge["name"])

            # Check if the badge already exists in the database
            current_badge = db_session.query(Badges).filter_by(
                name=badge["name"]
            )

            # Convert all the fields to strings using dict comprehension
            fields = {k: str(v) for k, v in badge.items()}

            if current_badge.first() is None:
                print("Badge does not exist in database")
                badge = Badges(**fields)
                db_session.add(badge)
                db_session.commit()
            else:
                print("Badge already exists -- updating")
                # Update the badge in the database
                current_badge.update(values=fields)
                db_session.commit()
    except Exception as e:
        print(str(e))
        # Rollback the changes to the database
        db_session.rollback()
        raise e


def sync_assertions(settings: Settings, db_session: Session):
    # Get all assertions from the badgr API
    bt = badgr_bearer_token(settings)
    try:
        assertions = get_all_assertions(bt, settings)
        assertionlst = assertions.json()["result"]
    except Exception as e:
        print(str(e))
        raise e

    # Loop through all assertions and add them to the assertions table
    try:
        for assertion in assertionlst:

            # Check if the assertion already exists in the database
            current_assertion = db_session.query(Assertions).filter_by(
                entityId=assertion["entityId"]
            )

            # Wrangle the fields to be compatible with the schema
            fields = wrangle_assertion(assertion, db_session=db_session)

            if current_assertion.first() is None:
                assertion = Assertions(**fields)
                print(
                    "Not in database - "
                    + assertion.recipient_plaintextIdentity
                    + " - "
                    + assertion.badgeclass
                )
                db_session.add(assertion)
                db_session.commit()
            else:
                print(
                    "Already in database (updating) - "
                    + fields["recipient_plaintextIdentity"]
                    + " - "
                    + fields["badgeclass"]
                )
                # Update the assertion in the database
                current_assertion.update(values=fields)
                db_session.commit()
    except Exception as e:
        print(str(e))
        # Rollback the changes to the database
        db_session.rollback()
        raise e
