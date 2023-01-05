from django import forms
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index

from staff.models import Course


class CoursePage(Page):
    intro = RichTextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)

    search_fields = Page.search_fields + [
        index.FilterField('intro'),
        index.SearchField('intro'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('course', widget=forms.Select),
        FieldPanel('intro')
    ]
