from datetime import date
from django.utils.crypto import get_random_string
import factory

from authentication.tests.factories.student_user_factory import StudentUserFactory
from payment.models import ReferralCoupon


class ReferralCouponFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReferralCoupon

    code = get_random_string(length=6)
    start_date = date.today()
    end_date = None
    description = None
    referrer = factory.SubFactory(StudentUserFactory)

    @factory.post_generation
    def effects(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.groups.add(*extracted)
