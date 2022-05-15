## Notifies the user via email
## Uses the Mail Chimp (mandrill) API
from app.config import MANDRILL_API_KEY
import mailchimp_transactional as MailchimpTransactional
from mailchimp_transactional.api_client import ApiClientError

def send_email(
    email_address: str,
    recipient_name: str, 
    subject: str, 
    message: str
):
    """
    Sends an email via Mandrill
    """
    try:
        mailchimp = MailchimpTransactional.Client(MANDRILL_API_KEY)
        response = mailchimp.messages.send(body={
            'message': {
                'subject': subject,
                'from_email': 'brnbot@bioresnet.org',
                'from_name': 'BRN Bot 🤖',
                'to': [{
                    'email': email_address,
                    'name': recipient_name,
                    'type': 'to'
                }],
                'html': message
            }
        })
        print('Mail Chimp API called successfully: {}'.format(response))
    except ApiClientError as error:  # pragma: no cover
        print('An exception occurred: {}'.format(error.text))


def html_parse_py(html: str, **kwargs):
    """
    Helper function to parse html templates and insert variables into them
    """
    for kwarg in kwargs.keys():
        html = html.replace("{{"+str(kwarg)+"}}", kwargs[kwarg])
    return html


def successful_register_notify(
    email: str,
    first_name: str,
    last_name: str,
    github_username: str
):
    """
    Sends an email to the user when they successfully register
    """
    message=open("s3_data/html_templates/welcome_email.html").read().strip()
    message = html_parse_py(message, **{
        'first_name': first_name,
        'last_name': last_name,
        'github_username': github_username,
        "email": email
    })
    send_email(email_address=email, recipient_name=first_name, subject='Welcome to the BRN Skill Assessment Program 🏆', message=message)
