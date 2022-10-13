from pytest_factoryboy import register

from authentication.tests.factories.user_factory import UserFactory
from staff.tests.factories.batch_factory import BatchFactory
from staff.tests.factories.course_factory import CourseFactory

register(BatchFactory)
register(CourseFactory)
register(UserFactory)
