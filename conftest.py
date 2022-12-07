from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
import pytest
from pytest_factoryboy import register
from wagtail.models import Locale, Site

from authentication.tests.factories.student_user_factory import StudentUserFactory
from authentication.tests.factories.user_factory import UserFactory
from payment.tests.factories.referral_coupon_factory import ReferralCouponFactory
from payment.tests.factories.coupon_effect_factory import CouponEffectFactory
from staff.tests.factories.batch_factory import BatchFactory
from staff.tests.factories.batch_page_factory import BatchPageFactory
from staff.tests.factories.batch_schedule_factory import BatchScheduleFactory
from staff.tests.factories.course_factory import CourseFactory
from staff.tests.factories.course_page_factory import CoursePageFactory
from staff.tests.factories.section_factory import SectionFactory
from student.tests.factories.certificate_factory import CertificateFactory
from student.tests.factories.enrolment_factory import EnrolmentFactory
from student.tests.factories.registration_factory import RegistrationFactory

register(BatchFactory)
register(BatchPageFactory)
register(BatchScheduleFactory)
register(CertificateFactory)
register(CouponEffectFactory)
register(CourseFactory)
register(CoursePageFactory)
register(EnrolmentFactory)
register(ReferralCouponFactory)
register(RegistrationFactory)
register(SectionFactory)
register(StudentUserFactory)
register(UserFactory)

client = Client

##################
# AUTHENTICATION #
##################

@pytest.fixture()
def existing_user():
    User = get_user_model()
    existing_user = User.objects.create_user(
        email='user@domain.com',
        first_name='FirstName',
        last_name='LastName',
        password=settings.PLACEHOLDER_PASSWORD
    )

    yield existing_user

#########
# BATCH #
#########

@pytest.fixture()
def coding_basics_batch(batch_factory, section_factory, batch_schedule_factory):
    coding_basics_batch = batch_factory()
    section_factory(batch=coding_basics_batch)
    batch_schedule_factory(batch=coding_basics_batch)

    yield coding_basics_batch

@pytest.fixture()
def coding_bootcamp_batch(batch_factory, course_factory, section_factory, batch_schedule_factory):
    coding_bootcamp_batch = batch_factory(course=course_factory(coding_bootcamp=True))
    coding_bootcamp_batch.price = 7999
    section_factory(batch=coding_bootcamp_batch)
    batch_schedule_factory(batch=coding_bootcamp_batch)

    yield coding_bootcamp_batch

@pytest.fixture()
def swe_fundamentals_batch(batch_factory, course_factory, section_factory, batch_schedule_factory):
    swe_fundamentals_batch = batch_factory(course=course_factory(swe_fundamentals=True))
    section_factory(batch=swe_fundamentals_batch)
    batch_schedule_factory(batch=swe_fundamentals_batch)

    yield swe_fundamentals_batch

###################
# COUPON EFFECT #
###################

@pytest.fixture()
def swe_fundamentals_coupon_effect(coupon_effect_factory, course_factory):
    swe_fundamentals_course = course_factory(swe_fundamentals=True)
    swe_fundamentals_coupon_effect = coupon_effect_factory(
        dollars_off=True,
        discount_amount=20,
        couponable_id=swe_fundamentals_course.id,
        couponable_type=type(swe_fundamentals_course).__name__
    )

    yield swe_fundamentals_coupon_effect

@pytest.fixture()
def coding_bootcamp_coupon_effect(coupon_effect_factory, course_factory):
    coding_bootcamp_course = course_factory(coding_bootcamp=True)
    coding_bootcamp_coupon_effect = coupon_effect_factory(
        dollars_off=True,
        discount_amount=200,
        couponable_id=coding_bootcamp_course.id,
        couponable_type=type(coding_bootcamp_course).__name__
    )

    yield coding_bootcamp_coupon_effect

################
# REGISTRATION #
################

@pytest.fixture()
def coding_basics_registration(coding_basics_batch, registration_factory):
    coding_basics_registration = registration_factory(
        batch=coding_basics_batch,
        course=coding_basics_batch.course
    )

    yield coding_basics_registration

@pytest.fixture()
def coding_bootcamp_registration(coding_bootcamp_batch, registration_factory):
    coding_bootcamp_registration = registration_factory(
        batch=coding_bootcamp_batch,
        course=coding_bootcamp_batch.course
    )

    yield coding_bootcamp_registration

@pytest.fixture()
def swe_fundamentals_registration(swe_fundamentals_batch, registration_factory):
    swe_fundamentals_registration = registration_factory(
        batch=swe_fundamentals_batch,
        course=swe_fundamentals_batch.course
    )

    yield swe_fundamentals_registration

@pytest.fixture()
def swe_fundamentals_registration_early_bird(swe_fundamentals_batch, registration_factory):
    swe_fundamentals_batch.start_date = date.today() + timedelta(days=21)
    swe_fundamentals_batch.end_date = date.today() + timedelta(days=22)
    swe_fundamentals_batch.save()

    swe_fundamentals_registration_early_bird = registration_factory(
        batch=swe_fundamentals_batch,
        course=swe_fundamentals_batch.course,
    )

    yield swe_fundamentals_registration_early_bird

###########
# WAGTAIL #
###########

@pytest.fixture()
def wagtail_site():
    Locale.objects.create(language_code='en')
    wagtail_site = Site(is_default_site=True)

    yield wagtail_site
