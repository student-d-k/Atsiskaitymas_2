import os
from flask import render_template, url_for, current_app
from flask_mail import Message
from Misc.my_logger import my_logger
from flask_mail import Mail
from dotenv import load_dotenv

env_file = '.env.prod' if os.getenv('FLASK_ENV') == 'production' else '.env.dev'
load_dotenv(dotenv_path=env_file)


def send_verification_email(user):
    'Send a verification email to the user.'
    current_app.config['SECRET_KEY'] = 'your-secret-key'
    current_app.config['PREFERRED_URL_SCHEME'] = 'http://'
    current_app.config['SERVER_NAME'] = '127.0.0.1:5004'
    current_app.config['APPLICATION_ROOT'] = '/'
    with current_app.app_context():
        verification_url = url_for('verify_email', token=user.token, _external=True)
    # mail settings
    current_app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    current_app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 2525))  # default to 2525 if not set
    current_app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    current_app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
    current_app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    current_app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    current_app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@gmail.com'
    mail = Mail(current_app)
    # Create the email message
    subject = 'Email Verification'
    # to_email = 'daumantas.kudzma@codeacademylt.onmicrosoft.com'
    to_email = user.email
    from_email = current_app.config['MAIL_DEFAULT_SENDER']
    html_content = render_template('verify_email.html', user_first_name=user.first_name, verification_url=verification_url)
    text_content = f'Please verify your email address by clicking the following link: {verification_url}'

    # Prepare the message
    msg = Message(
        subject=subject,
        recipients=[to_email],
        html=html_content,
        body=text_content,
        sender=from_email
    )
    # Send the email
    my_logger.info(f'Sending email {text_content} to {to_email}')
    try:
        mail.send(msg)
        my_logger.info(f'Verification email sent to {user.email}')
    except Exception as e:
        my_logger.error(f'Failed to send email: {e}')
        return str(e)
