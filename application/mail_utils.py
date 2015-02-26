from flask.ext.mail import Mail, Message
from application import app

mail = Mail(app)

def create_message(subject, recipient):
    """Returns a message after setting it's subject, sender and receiver."""
    msg = Message(subject, sender='no-reply@evaluator.in', recipients=[recipient])
    return msg
