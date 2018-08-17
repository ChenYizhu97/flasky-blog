from threading import Thread
from flask import render_template, current_app
from flask_mail import Message

from . import mail

def send_mail(to, subject, template, **kwargs):
    context = current_app.app_context()
    msg = Message(subject=current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                sender=current_app.config['FLASKY_MAIL_SENDER'], 
                recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_mail, args=[msg, context])
    thr.start()
    return thr
    
def send_async_mail(msg, context):
    with context:
        mail.send(msg)