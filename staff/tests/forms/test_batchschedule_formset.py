from django.urls import reverse
import pytest

from staff.forms import BatchScheduleFormSet

pytestmark = pytest.mark.django_db

class TestBatchScheduleFormSet:
    def test_empty_form_is_invalid(self):
        batch_schedule_formset = BatchScheduleFormSet(
            data={
                'batch-schedule-TOTAL_FORMS': '1',
                'batch-schedule-INITIAL_FORMS': '0',
                'batch-schedule-MIN_NUM_FORMS': '0',
                'batch-schedule-MAX_NUM_FORMS': '7',
                'batch-schedule-0-day': '',
                'batch-schedule-0-start_time': '',
                'batch-schedule-0-end_time': '',
            },
            prefix='batch-schedule'
        )

        outcome = batch_schedule_formset.is_valid()

        assert outcome is False

    def test_complete_form_is_valid(self):
        batch_schedule_formset = BatchScheduleFormSet(
            data={
                'batch-schedule-TOTAL_FORMS': '2',
                'batch-schedule-INITIAL_FORMS': '0',
                'batch-schedule-MIN_NUM_FORMS': '0',
                'batch-schedule-MAX_NUM_FORMS': '7',
                'batch-schedule-0-day': 'MON',
                'batch-schedule-0-start_time': '00:00',
                'batch-schedule-0-end_time': '00:01',
                'batch-schedule-1-day': 'THU',
                'batch-schedule-1-start_time': '00:00',
                'batch-schedule-1-end_time': '00:01'
            },
            prefix='batch-schedule'
        )

        outcome = batch_schedule_formset.is_valid()
        print(batch_schedule_formset)

        assert outcome is True

    def test_start_time_should_be_before_end_time(self):
        invalid_start_time = '00:01'
        invalid_end_time = '00:00'
        batch_schedule_formset = BatchScheduleFormSet(
            data={
                'batch-schedule-TOTAL_FORMS': '1',
                'batch-schedule-INITIAL_FORMS': '0',
                'batch-schedule-MIN_NUM_FORMS': '0',
                'batch-schedule-MAX_NUM_FORMS': '7',
                'batch-schedule-0-day': 'MON',
                'batch-schedule-0-start_time': invalid_start_time,
                'batch-schedule-0-end_time': invalid_end_time,
                'batch-schedule-1-day': 'THU',
                'batch-schedule-1-start_time': '02:00',
                'batch-schedule-1-end_time': '04:00'
            },
            prefix='batch-schedule'
        )

        outcome = batch_schedule_formset.is_valid()

        assert outcome is False
        assert 'Start time must be before end time' in batch_schedule_formset.errors[0]['start_time']
