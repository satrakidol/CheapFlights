from project.make_celery import celery_app as celery
from flask_mail import Mail, Message
# from . import mail

@celery.task()
def print_hello():
    print("Hello from task")

mail = Mail() 

maria = 'kor'

@celery.task()
def email():
    message = Message(
        subject = "New cheaper flight for your destination",
        recipients = ['ap22017@hua.gr'],
        sender='CheapFlights',
    )
    message.body = maria
    mail.send(message)

    return "sent"