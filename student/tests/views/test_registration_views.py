from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client
from django.urls import reverse
from django.utils.timezone import make_aware
import pytest

from payment.models.coupon import Coupon
from payment.models.coupon_effect import CouponEffect
from staff.models import Batch, Course, Section
from student.models.registration import Registration

pytestmark = pytest.mark.django_db
client = Client()
User = get_user_model()

existing_user_email = 'existing_user@email.com'
existing_user_first_name = 'Existing'
existing_user_last_name = 'User'
existing_user_password = settings.PLACEHOLDER_PASSWORD


@pytest.fixture()
def existing_user():
    existing_user = User.objects.create(
        email=existing_user_email,
        first_name=existing_user_first_name,
        last_name=existing_user_last_name,
        password=existing_user_password
    )

    yield existing_user

@pytest.fixture()
def registration(batch_factory):
    batch = batch_factory()
    Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )
    registration = Registration.objects.create(
        course=batch.course,
        batch=batch,
        first_name='FirstName',
        last_name='LastName',
        email='user@email.com',
        country_of_residence='SG',
        referral_channel='word_of_mouth',
    )

    yield registration

@pytest.fixture()
def early_bird_registration(batch_factory):
    start_date = date.today() + timedelta(days=21)
    batch = batch_factory(
        start_date=start_date,
        end_date=start_date + timedelta(days=1)
    )
    Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )
    early_bird_registration = Registration.objects.create(
        course=batch.course,
        batch=batch,
        first_name='FirstName',
        last_name='LastName',
        email='user@email.com',
        country_of_residence='SG',
        referral_channel='word_of_mouth',
    )
    return early_bird_registration

def test_registration_form_renders_batch_on_start_date(batch_factory):
    batch = batch_factory()
    Section.objects.create(
        batch=batch,
        number=1,
        capacity=1
    )

    response = client.get(reverse('basics_register'))

    assert response.status_code == 200
    assert 'id="id_batch_selection-batch_0"' in str(response.content)


def test_registration_wizard_form_existing_user(batch_factory, existing_user):
    batch = batch_factory()
    batch_selection_form_response = client.post(reverse('basics_register'), {
        'registration_wizard-current_step': 'batch_selection',
        'batch_selection-batch': '1',
    })
    student_info_form_response = client.post(reverse('basics_register'), {
        'registration_wizard-current_step': 'student_info',
        'student_info-first_name': existing_user_first_name,
        'student_info-last_name': existing_user_last_name,
        'student_info-email': existing_user_email,
        'student_info-country_of_residence': 'SG',
        'student_info-referral_channel': 'word_of_mouth',
    })

    assert batch_selection_form_response.status_code == HttpResponse.status_code
    assert student_info_form_response.status_code == HttpResponseRedirect.status_code
    registration = Registration.objects.get(email=existing_user_email)
    assert registration.batch == batch
    assert User.objects.all().count() == 1


def test_registration_wizard_form_new_user(batch_factory, existing_user):
    batch_factory()
    client.post(reverse('basics_register'), {
        'registration_wizard-current_step': 'batch_selection',
        'batch_selection-batch': '1',
    })
    client.post(reverse('basics_register'), {
        'registration_wizard-current_step': 'student_info',
        'student_info-first_name': 'New',
        'student_info-last_name': 'User',
        'student_info-email': 'new_user@email.com',
        'student_info-country_of_residence': 'SG',
        'student_info-referral_channel': 'facebook',
    })

    assert User.objects.all().count() == 2

def test_payment_preview_get_renders_original_price_if_no_valid_referral_code_no_early_bird(registration):
    response = client.get(
        reverse(
            'basics_register_payment_preview',
            kwargs={
                'registration_id': registration.id
            }
        )
    )

    assert response.status_code == 200
    assert response.context['original_payable_amount'] == 199
    assert response.context['stripe_coupon_id'] is None
    assert response.context['final_payable_amount'] == 199

def test_payment_preview_get_passes_stripe_coupon_id_to_render_if_referral_code_valid_no_early_bird(registration, mocker):
    coupon_effect = CouponEffect.objects.create(
        couponable_type=type(registration.batch.course).__name__,
        couponable_id=registration.batch.course.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )
    coupon = Coupon.objects.create(start_date=make_aware(datetime.now()),)
    coupon.effects.set([coupon_effect])
    registration.referral_code = coupon.code
    registration.save()
    stripe_coupon_id = 'Z4OV52SU'
    mocker.patch(
        'payment.library.stripe.Stripe.create_coupon',
        return_value={
            'id': stripe_coupon_id,
            'object': 'coupon',
            'amount_off': 10,
            'created': 1660146918,
            'currency': 'sgd',
            'duration': 'forever',
            'livemode': False,
            'max_redemptions': None,
            'metadata': {},
            'name': 'SGD 10.00 off',
            'percent_off': None,
            'redeem_by': None,
            'times_redeemed': 0,
            'valid': True
        }
    )

    response = client.get(
        reverse(
            'basics_register_payment_preview',
            kwargs={
                'registration_id': registration.id
            }
        )
    )

    assert response.status_code == 200
    assert response.context['original_payable_amount'] == 199
    assert response.context['stripe_coupon_id'] == stripe_coupon_id
    assert response.context['final_payable_amount'] == 189

def test_payment_preview_get_renders_early_bird_price_without_valid_referral_code(early_bird_registration, mocker):
    stripe_coupon_id = 'Z4OV52SU'
    mocker.patch(
        'payment.library.stripe.Stripe.create_coupon',
        return_value={
            'id': stripe_coupon_id,
            'object': 'coupon',
            'amount_off': 10,
            'created': 1660146918,
            'currency': 'sgd',
            'duration': 'forever',
            'livemode': False,
            'max_redemptions': None,
            'metadata': {},
            'name': 'SGD 10.00 off',
            'percent_off': None,
            'redeem_by': None,
            'times_redeemed': 0,
            'valid': True
        }
    )

    response = client.get(
        reverse(
            'basics_register_payment_preview',
            kwargs={
                'registration_id': early_bird_registration.id
            }
        )
    )

    assert response.status_code == 200
    assert response.context['original_payable_amount'] == 199
    assert response.context['stripe_coupon_id'] == stripe_coupon_id
    assert response.context['final_payable_amount'] == 189

def test_payment_preview_get_renders_early_bird_price_with_valid_referral_code(early_bird_registration, mocker):
    coupon_effect = CouponEffect.objects.create(
        couponable_type=type(early_bird_registration.batch.course).__name__,
        couponable_id=early_bird_registration.batch.course.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )
    coupon = Coupon.objects.create(start_date=make_aware(datetime.now()),)
    coupon.effects.set([coupon_effect])
    early_bird_registration.referral_code = coupon.code
    early_bird_registration.save()
    stripe_coupon_id = 'Z4OV52SU'
    mocker.patch(
        'payment.library.stripe.Stripe.create_coupon',
        return_value={
            'id': stripe_coupon_id,
            'object': 'coupon',
            'amount_off': 20,
            'created': 1660146918,
            'currency': 'sgd',
            'duration': 'forever',
            'livemode': False,
            'max_redemptions': None,
            'metadata': {},
            'name': 'SGD 10.00 off',
            'percent_off': None,
            'redeem_by': None,
            'times_redeemed': 0,
            'valid': True
        }
    )

    response = client.get(
        reverse(
            'basics_register_payment_preview',
            kwargs={
                'registration_id': early_bird_registration.id
            }
        )
    )

    assert response.status_code == 200
    assert response.context['original_payable_amount'] == 199
    assert response.context['stripe_coupon_id'] == stripe_coupon_id
    assert response.context['final_payable_amount'] == 179
