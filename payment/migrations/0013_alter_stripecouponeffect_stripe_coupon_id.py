# Generated by Django 4.0.5 on 2022-08-05 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0012_stripecouponeffect'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripecouponeffect',
            name='stripe_coupon_id',
            field=models.CharField(max_length=8, null=True),
        ),
    ]
