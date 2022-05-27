from django.db import models
from django.conf import settings
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class Correspondence(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    content = models.TextField()
    receiver = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def send_basics_registration_confirmation_email(self, student_email, student_first_name, batch_number, batch_start_date, batch_course_name):
        # content of email
        html_content = '''<h2 > Welcome to Rocket Academy!< /h2 >
                            <h4 > Hi {{first_name}}, < /h4 >
                            <p >
                            You have been registered into {{batch.course.name | title}} - {{batch.number}}!
                            </p >

                            <p >
                            Our classes will begin on {{batch.start_date}} from 7.30pm to 9.30pm
                            </p >
                            <p >
                            <strong >
                            Prior to our first session, please join our Slack Channel using the SAME EMAIL ADDRESS you used to register on our website, with this link here.
                            </strong >
                            </p >
                            <a href = "https://join.slack.com/t/rocketacademybasics/shared_invite/zt-174hul8rn-Hl5Tt1NHYZuJGLnhNHbiaA" > https: // join.slack.com/t/rocketacademybasics/shared_invite/zt-174hul8rn-Hl5Tt1NHYZuJGLnhNHbiaA < /a >
                            </p >
                            <p >
                            Further communications with regards to Basics will be shared with you on Slack such as:
                            </p >
                            <ul >
                            <li >
                            Required software and setup
                            </li >
                            <li >
                            Basics Groups
                            </li >
                            <li >
                            Zoom Links to your classroom
                            </li >
                            </ul >

                            <strong >
                            Thank you again for your support with Rocket Academy,
                            We look forward to seeing you in class!
                            </strong >'''
        # sender email address
        rocket_email = settings.ROCKET_EMAIL_ADDRESS
        template_id = 'd-0fc0a2398ba044a0b5015a528460bd3d'

        try:
            message = Mail(
                from_email=rocket_email,
                to_emails=student_email,
                subject='Your registration has been confirmed',
            )

            message.dynamic_template_data = {
                'first_name': student_first_name,
                'course_name': batch_course_name,
                'number': batch_number,
                'start_date': batch_start_date
            }
            message.template_id = template_id
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
        except Exception as e:
            print(e.message)
        else:
            new_correspondence = Correspondence(
                content=html_content,
                receiver=student_email
            )

            new_correspondence.save()
            return new_correspondence
