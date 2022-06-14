# Generated by Django 4.0.5 on 2022-06-10 02:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('authentication', '0002_user_groups_user_is_admin_user_is_staff_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('hubspot_contact_id', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
            bases=('authentication.user',),
        ),
        migrations.AddField(
            model_name='user',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype'),
        ),
    ]
