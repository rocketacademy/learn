# Generated by Django 4.1.2 on 2023-01-14 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0015_alter_course_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='price_hk',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
