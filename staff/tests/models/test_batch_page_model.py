import pytest

pytestmark = pytest.mark.django_db


def test_batch_number_assigned_as_slug(wagtail_site, batch_page_factory):
    batch_page = batch_page_factory.create(swe_fundamentals=True)

    assert batch_page.slug == str(batch_page.batch.number)
