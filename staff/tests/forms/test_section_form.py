import pytest

from staff.forms import SectionForm

pytestmark = pytest.mark.django_db

class TestSectionForm:
    def test_empty_form_is_invalid(self):
        section_form = SectionForm(data={})

        outcome = section_form.is_valid()

        assert outcome is False

    def test_capacity_should_be_at_least_one(self):
        section_form = SectionForm(
            data={
                'capacity': 0,
            }
        )

        outcome = section_form.is_valid()

        assert outcome is False
        assert 'Capacity per section should be more than one' in section_form.errors['capacity']
