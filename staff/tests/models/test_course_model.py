import pytest

pytestmark = pytest.mark.django_db


def test_string_representation(course_factory):
    swe_fundamentals_course = course_factory(swe_fundamentals=True)

    string_representation = swe_fundamentals_course.__str__()

    assert string_representation == swe_fundamentals_course.get_name_display()
