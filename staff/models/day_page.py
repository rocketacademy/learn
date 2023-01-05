from django import forms
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index

from staff.models import BatchPage


class DayPage(Page):
    batch_page = models.ForeignKey(BatchPage, on_delete=models.PROTECT)
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.FilterField('body'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('batch_page', widget=forms.Select),
        FieldPanel('body')
    ]
