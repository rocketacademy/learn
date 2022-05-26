from django.db import models
import pytz
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel

from staff.models.batch import Batch


class Registration(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    WORD_OF_MOUTH = 'word_of_mouth'
    LINKEDIN = 'linkedin'
    GOOGLE = 'google'
    FACEBOOK = 'facebook'
    YOUTUBE = 'youtube'
    INSTAGRAM = 'instagram'

    REFERRAL_CHANNELS = [
        (WORD_OF_MOUTH, 'Word of mouth'),
        (LINKEDIN, 'LinkedIn'),
        (GOOGLE, 'Google'),
        (FACEBOOK, 'Facebook'),
        (YOUTUBE, 'YouTube'),
        (INSTAGRAM, 'Instagram'),
    ]

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    country_of_residence = models.CharField(max_length=255, choices=pytz.country_names.items())
    referral_channel = models.CharField(max_length=255, choices=REFERRAL_CHANNELS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
