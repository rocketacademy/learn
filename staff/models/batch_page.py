from django import forms
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index

from staff.models import Batch


class BatchPage(Page):
    intro = RichTextField(blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT)

    search_fields = Page.search_fields + [
        index.FilterField('intro'),
        index.SearchField('intro'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('batch', widget=forms.Select),
        FieldPanel('intro')
    ]

    def save(self, *args, **kwargs):
        # slug does not appear above as an attribute
        # because it is an attribute on Wagtail's Page model
        self.slug = self.batch.number

        return super().save(*args, **kwargs)
