import factory

from payment.models import CouponEffect

class CouponEffectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CouponEffect

    couponable_type = None
    couponable_id = None
    discount_type = CouponEffect.DOLLARS
    discount_amount = 10

    class Params:
        dollars_off = factory.Trait(
            discount_type=CouponEffect.DOLLARS
        )

        percent_off = factory.Trait(
            discount_type=CouponEffect.PERCENTAGE
        )
