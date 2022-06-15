from django.db import models
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel
from .batch import Batch

class Section(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField()
    slack_channel_id = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def next_number(self, batch_id):
        if self.objects.count() == 0:
            return 1
        return self.objects.filter(batch__id=batch_id).aggregate(models.Max('number'))['number__max'] + 1

    def fully_enrolled(self):
        if self.enrolment_set.count() >= self.capacity:
            return True
        return False
