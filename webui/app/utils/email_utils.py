# Notifies the user via email
# Uses the Mail Chimp (mandrill) API
from app.config import settings
from datetime import datetime, timedelta
from app import models, crud, db
import secrets
from flask import render_template
import mailchimp_transactional as MailchimpTransactional
from mailchimp_transactional.api_client import ApiClientError


def send_email(
    email_address: str, recipient_name: str, subject: str, message: str
):
    """
    Sends an email via Mandrill
    """
    try:
        mailchimp = MailchimpTransactional.Client(settings.MANDRILL_API_KEY)
        mailchimp.messages.send(
            body={
                "message": {
                    "subject": subject,
                    "from_email": "brnbot@bioresnet.org",
                    "from_name": "BRN Bot 🤖",
                    "to": [
                        {
                            "email": email_address,
                            "name": recipient_name,
                            "type": "to",
                        }
                    ],
                    "html": message,
                }
            }
        )
    except ApiClientError as error:  # pragma: no cover
        print("An exception occurred: {}".format(error.text))


def send_verification_email(db: db.db_session, user: models.Users):
    verification_code = secrets.token_urlsafe(8)
    # Add to the database
    crud.add_email_verification_code(
        db,
        user=user,
        verification_code=verification_code,
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    send_email(
        email_address=user.email,
        recipient_name=user.first_name + " " + user.last_name,
        subject="Your verification code",
        message=render_template(
            "verification_email.html",
            code=verification_code,
            aws_url=settings.AWS_PUBLIC_S3_URL,
        ),
    )


def send_welcome_email(user: models.Users):
    send_email(
        email_address=user.email,
        recipient_name=user.first_name + " " + user.last_name,
        subject="Welcome to BRN Skill Assessments 🏆",
        message=render_template(
            "welcome_email.html", user=user, site_url=settings.SITE_URL
        ),
    )
