# Generated by Django 4.1.2 on 2022-10-10 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0009_enrolment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrolment',
            name='deleted_at',
            field=models.DateTimeField(db_index=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='deleted_at',
            field=models.DateTimeField(db_index=True, editable=False, null=True),
        ),
    ]
