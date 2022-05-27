from django.conf import settings
import datetime
import json
from emails.models import Correspondence
from authentication.models import User
import pytest

# Create your tests here.


class TestCorrespondenceCreation:

    def test_increase_in_total_correspondence(self):
        new_correspondence = Correspondence.objects.create(
            content='<h1>Welcome to Rocket Academy!</h1>',
            receiver='michelle@rocketacademy.co',
        )

        assert Correspondence.objects.all.count() == 1
        assert new_correspondence.receiver == 'michelle@rocketacademy.co'
