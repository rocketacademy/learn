# Generated by Django 4.0.5 on 2022-07-08 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_alter_coupon_code_alter_coupon_couponable_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='description',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
