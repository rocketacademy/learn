from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
import pytest
from pytest_factoryboy import register

from authentication.tests.factories.user_factory import UserFactory
from staff.tests.factories.batch_factory import BatchFactory
from staff.tests.factories.batch_schedule_factory import BatchScheduleFactory
from staff.tests.factories.course_factory import CourseFactory
from staff.tests.factories.section_factory import SectionFactory

register(BatchFactory)
register(BatchScheduleFactory)
register(CourseFactory)
register(SectionFactory)
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
