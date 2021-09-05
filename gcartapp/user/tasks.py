from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import EmailMessage


@shared_task
def send_mail_task(mail_subject, message, to_email, from_email):
    send_email = EmailMessage(
        mail_subject, message, to=[to_email], from_email=from_email
    )
    send_email.send()
    return None
