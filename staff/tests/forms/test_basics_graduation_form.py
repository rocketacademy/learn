import datetime
from django.conf import settings
import pytest
from authentication.models.student_user import StudentUser

from staff.forms import BasicsGraduationForm, basics_graduation
from staff.models import Batch, Course, Section
from student.models.enrolment import Enrolment
from student.models.registration import Registration

pytestmark = pytest.mark.django_db

@pytest.fixture()
def batch():
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(35)
    course = Course.objects.create(name=settings.CODING_BASICS)
    batch = Batch.objects.create(
        course=course,
        start_date=start_date,
        end_date=end_date,
        capacity=90,
        sections=5
    )

    yield batch

class TestBasicsGraduationForm:
    def test_empty_form_is_valid(self, batch):
        basics_graduation_form = BasicsGraduationForm(data={}, batch_id=batch.id)

        outcome = basics_graduation_form.is_valid()

        assert outcome is True

    def test_form_contains_checkboxes_for_enrolled_student_users(self, batch):
        section = Section.objects.create(
            batch=batch,
            number=1,
            capacity=2
        )
        first_student_user = StudentUser.objects.create_user(
            first_name='First',
            last_name='Student',
            email='firststudent@example.com',
            password=settings.PLACEHOLDER_PASSWORD
        )
        first_registration = Registration.objects.create(
            course=batch.course,
            batch=batch,
            first_name=first_student_user.first_name,
            last_name=first_student_user.last_name,
            email=first_student_user.email,
            country_of_residence='SG',
            referral_channel='word_of_mouth'
        )
        first_enrolment = Enrolment.objects.create(
            registration=first_registration,
            batch=batch,
            section=section,
            student_user=first_student_user
        )
        second_student_user = StudentUser.objects.create_user(
            first_name='Second',
            last_name='Student',
            email='secondstudent@example.com',
            password=settings.PLACEHOLDER_PASSWORD
        )
        second_registration = Registration.objects.create(
            course=batch.course,
            batch=batch,
            first_name=second_student_user.first_name,
            last_name=second_student_user.last_name,
            email=second_student_user.email,
            country_of_residence='SG',
            referral_channel='word_of_mouth'
        )
        second_enrolment = Enrolment.objects.create(
            registration=second_registration,
            batch=batch,
            section=section,
            student_user=second_student_user
        )

        basics_graduation_form = BasicsGraduationForm(batch_id=batch.id)

        assert basics_graduation_form.fields['student_user'].choices == [
            (first_student_user.id, first_student_user),
            (second_student_user.id, second_student_user)
        ]
