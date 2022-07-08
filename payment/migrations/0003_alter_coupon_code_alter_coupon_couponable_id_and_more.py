# Generated by Django 4.0.5 on 2022-07-08 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_create_coupon_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='code',
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='couponable_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='couponable_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
