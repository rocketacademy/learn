# Generated by Django 4.1.2 on 2022-10-10 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0012_remove_certificate_student_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='batch',
            name='type',
            field=models.CharField(blank=True, choices=[('part_time', 'Part-time'), ('full_time', 'Full-time')], max_length=9, null=True),
        ),
        migrations.AlterField(
            model_name='batch',
            name='deleted_at',
            field=models.DateTimeField(db_index=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='batchschedule',
            name='deleted_at',
            field=models.DateTimeField(db_index=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='deleted_at',
            field=models.DateTimeField(db_index=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='deleted_at',
            field=models.DateTimeField(db_index=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='section',
            name='deleted_at',
            field=models.DateTimeField(db_index=True, editable=False, null=True),
        ),
    ]
