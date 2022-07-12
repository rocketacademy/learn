# Generated by Django 4.0.5 on 2022-07-08 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('code', models.CharField(max_length=6)),
                ('couponable_type', models.CharField(max_length=50)),
                ('couponable_id', models.IntegerField()),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('type', models.CharField(choices=[('referral', 'Referral')], max_length=20)),
                ('discount_type', models.CharField(choices=[('percent', 'Percent off'), ('dollars', 'Dollars off')], max_length=7)),
                ('discount_amount', models.IntegerField()),
                ('description', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
