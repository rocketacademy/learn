# Generated by Django 4.0.5 on 2022-08-29 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0008_alter_registration_referral_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrolment',
            name='status',
            field=models.CharField(choices=[('COMPLETED', 'Completed'), ('NOT_COMPLETED', 'Not completed')], default='NOT_COMPLETED', max_length=15),
            preserve_default=False,
        ),
    ]
