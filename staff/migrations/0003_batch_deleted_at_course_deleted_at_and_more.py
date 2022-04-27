# Generated by Django 4.0.4 on 2022-04-22 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0002_batchschedule_created_at_batchschedule_deleted_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='deleted_at',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='deleted_at',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='section',
            name='deleted_at',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='batchschedule',
            name='deleted_at',
            field=models.DateTimeField(editable=False, null=True),
        ),
    ]