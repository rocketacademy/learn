from freezegun import freeze_time
import pytest

from staff.forms import BatchForm

pytestmark = pytest.mark.django_db

class TestBatchForm:
    def test_empty_form_is_invalid(self):
        batch_form = BatchForm(data={})

        outcome = batch_form.is_valid()

        assert outcome is False

    def test_form_start_date_should_be_future_date(self):
        freezer = freeze_time('2022-01-01')
        batch_form = BatchForm(
            data={
                'start_date': '2021-12-31',
                'end_date': '2022-01-02'
            }
        )

        freezer.start()
        outcome = batch_form.is_valid()
        freezer.stop()

        assert outcome is False
        assert 'Start date should be in the future' in batch_form.errors['start_date']

    def test_form_start_date_should_be_before_end_date(self):
        freezer = freeze_time('2022-01-01')
        batch_form = BatchForm(
            data={
                'start_date': '2022-01-02',
                'end_date': '2021-12-31'
            }
        )

        freezer.start()
        outcome = batch_form.is_valid()
        freezer.stop()

        assert outcome is False
        assert 'Start date must be before end date' in batch_form.errors['start_date']
        assert 'Start date must be before end date' in batch_form.errors['end_date']

    def test_form_should_have_at_least_one_section(self):
        batch_form = BatchForm(
            data={
                'sections': 0,
            }
        )

        outcome = batch_form.is_valid()

        assert outcome is False
        assert 'Each batch should have at least one section' in batch_form.errors['sections']

    def test_form_section_capacity_should_be_at_least_one(self):
        batch_form = BatchForm(
            data={
                'section_capacity': 0,
            }
        )

        outcome = batch_form.is_valid()

        assert outcome is False
        assert 'Capacity per section should be more than one' in batch_form.errors['section_capacity']
