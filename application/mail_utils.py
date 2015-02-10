from flask.ext.sendmail import Mail, Message
from application import app

mail = Mail(app)

def create_message(subject, recipient):
    """Returns a message after setting it's subject, sender and receiver."""
    msg = Message(subject)
    msg.sender = 'no-reply@evaluator.in'
    msg.add_recipient(recipient)
    return msg
