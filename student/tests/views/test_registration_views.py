from datetime import datetime
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client
from django.urls import reverse
from django.utils.timezone import make_aware
import pytest

from payment.models.coupon import Coupon
from payment.models.coupon_effect import CouponEffect
from student.models.registration import Registration

pytestmark = pytest.mark.django_db
client = Client()
User = get_user_model()


def test_registration_form_renders_batch_on_start_date(swe_fundamentals_batch):
    response = client.get(reverse('swe_fundamentals_register'))

    assert response.status_code == 200
    assert 'id="id_batch_selection-batch_0"' in str(response.content)


def test_registration_wizard_form_existing_user(swe_fundamentals_batch, existing_user):
    batch_selection_form_response = client.post(reverse('swe_fundamentals_register'), {
        'registration_wizard-current_step': 'batch_selection',
        'batch_selection-batch': '1',
    })
    student_info_form_response = client.post(reverse('swe_fundamentals_register'), {
        'registration_wizard-current_step': 'student_info',
        'student_info-first_name': existing_user.first_name,
        'student_info-last_name': existing_user.last_name,
        'student_info-email': existing_user.email,
        'student_info-country_of_residence': 'SG',
        'student_info-referral_channel': 'word_of_mouth',
    })

    assert batch_selection_form_response.status_code == HttpResponse.status_code
    assert student_info_form_response.status_code == HttpResponseRedirect.status_code
    registration = Registration.objects.get(email=existing_user.email)
    assert registration.batch == swe_fundamentals_batch
    assert User.objects.all().count() == 1


def test_registration_wizard_form_new_user(swe_fundamentals_batch, existing_user):
    client.post(reverse('swe_fundamentals_register'), {
        'registration_wizard-current_step': 'batch_selection',
        'batch_selection-batch': '1',
    })
    client.post(reverse('swe_fundamentals_register'), {
        'registration_wizard-current_step': 'student_info',
        'student_info-first_name': 'New',
        'student_info-last_name': 'User',
        'student_info-email': 'new_user@email.com',
        'student_info-country_of_residence': 'SG',
        'student_info-referral_channel': 'facebook',
    })

    assert User.objects.all().count() == 2

def test_payment_preview_get_renders_original_price_if_no_valid_referral_code_no_early_bird(swe_fundamentals_registration):
    response = client.get(
        reverse(
            'swe_fundamentals_register_payment_preview',
            kwargs={
                'registration_id': swe_fundamentals_registration.id
            }
        )
    )

    assert response.status_code == 200
    assert response.context['registration'] == swe_fundamentals_registration
    assert response.context['original_payable_amount'] == 199
    assert response.context['stripe_coupon_id'] is None
    assert response.context['final_payable_amount'] == 199

def test_payment_preview_get_passes_stripe_coupon_id_to_render_if_referral_code_valid_no_early_bird(swe_fundamentals_registration, mocker):
    coupon_effect = CouponEffect.objects.create(
        couponable_type=type(swe_fundamentals_registration.batch.course).__name__,
        couponable_id=swe_fundamentals_registration.batch.course.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )
    coupon = Coupon.objects.create(start_date=make_aware(datetime.now()),)
    coupon.effects.set([coupon_effect])
    swe_fundamentals_registration.referral_code = coupon.code
    swe_fundamentals_registration.save()
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
            'swe_fundamentals_register_payment_preview',
            kwargs={
                'registration_id': swe_fundamentals_registration.id
            }
        )
    )

    assert response.status_code == 200
    assert response.context['original_payable_amount'] == 199
    assert response.context['stripe_coupon_id'] == stripe_coupon_id
    assert response.context['final_payable_amount'] == 189

def test_payment_preview_get_renders_early_bird_price_without_valid_referral_code(swe_fundamentals_registration_early_bird, mocker):
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
            'swe_fundamentals_register_payment_preview',
            kwargs={
                'registration_id': swe_fundamentals_registration_early_bird.id
            }
        )
    )

    assert response.status_code == 200
    assert response.context['original_payable_amount'] == 199
    assert response.context['stripe_coupon_id'] == stripe_coupon_id
    assert response.context['final_payable_amount'] == 189

def test_payment_preview_get_renders_early_bird_price_with_valid_referral_code(swe_fundamentals_registration_early_bird, mocker):
    coupon_effect = CouponEffect.objects.create(
        couponable_type=type(swe_fundamentals_registration_early_bird.batch.course).__name__,
        couponable_id=swe_fundamentals_registration_early_bird.batch.course.id,
        discount_type=CouponEffect.DOLLARS,
        discount_amount=10
    )
    coupon = Coupon.objects.create(start_date=make_aware(datetime.now()),)
    coupon.effects.set([coupon_effect])
    swe_fundamentals_registration_early_bird.referral_code = coupon.code
    swe_fundamentals_registration_early_bird.save()
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
            'swe_fundamentals_register_payment_preview',
            kwargs={
                'registration_id': swe_fundamentals_registration_early_bird.id
            }
        )
    )

    assert response.status_code == 200
    assert response.context['original_payable_amount'] == 199
    assert response.context['stripe_coupon_id'] == stripe_coupon_id
    assert response.context['final_payable_amount'] == 179
