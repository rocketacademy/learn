import pytest

from staff.models import Course

pytestmark = pytest.mark.django_db


def test_course_page_assoicated_with_course(wagtail_site, course_page_factory):
    course_page = course_page_factory.create(swe_fundamentals=True)

    assert course_page.course == Course.objects.get(name=Course.SWE_FUNDAMENTALS)
