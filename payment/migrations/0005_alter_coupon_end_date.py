# Generated by Django 4.0.5 on 2022-07-08 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_alter_coupon_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
