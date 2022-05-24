from django.shortcuts import render
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_registration_confirmation_email(student_email):

    message = Mail(
        from_email='hello@rocketacademy.co',
        to_emails=student_email,
        subject='Your registration has been confirmed',
        html_content='<strong>Thank you for registering for Codind Basics!</strong>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
