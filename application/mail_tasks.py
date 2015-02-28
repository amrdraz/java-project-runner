import xkcdpass.xkcd_password as xp
from application.mail_utils import mail, Message, create_message
from application.models import User
from application import app, db
from flask import render_template


def random_password(user_id):
    """Sends a new password after generating it."""
    try:
        user = User.objects.get(id=user_id)
        wordfile = xp.locate_wordfile()
        mywords = xp.generate_wordlist(
            wordfile=wordfile, min_length=5, max_length=10)
        password = xp.generate_xkcdpassword(mywords)
        user.password = password
        user.save()
        msg = create_message('Your new password', user.email)
        context = {'user': user.to_dict(), 'password': password}
        msg.body = render_template('emails/pass.txt', **context)
        mail.send(msg)
    except (db.DoesNotExist):
        app.logger.warning(
            'Attempted to send new password to non existing user.')

def reset_password(user_id):
    """Sends an email to confirm user password reset."""
    try:
        user = User.objects.get(id=user_id)
        reset_token = user.generate_pass_reset_token()
        reset_url = 'https://evaluator.in/#/reset/?token={0}'.format(reset_token)
        msg = create_message('Password reset', user.email)
        context = {'user': user.to_dict(), 'reset_url': reset_url}
        msg.body = render_template('emails/reset.txt', **context)
        mail.send(msg)
    except (db.DoesNotExist):
        app.logger.warning('Attempted to reset password of non existing user')


def activate_account(user_id):
    try:
        user = User.objects.get(id=user_id)
        # Generate link
        activation_token = user.generate_activation_token()
        activation_url = 'https://evaluator.in/#/activate/?token={0}'.format(
            activation_token)
        # send email
        msg = create_message("Activate your evaluator.in account", user.email)
        context = {'user': user.to_dict(), 'activation_url': activation_url}
        msg.body = render_template('emails/activation.txt', **context)
        mail.send(msg)
    except (db.DoesNotExist):
        app.logger.warning('Attempted to send mail to non existing user.')
