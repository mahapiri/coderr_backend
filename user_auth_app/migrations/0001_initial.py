# Generated by Django 5.2.1 on 2025-05-22 09:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
                ('location', models.CharField(max_length=255)),
                ('tel', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('working_hours', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('business', 'Business'), ('customer', 'Customer')], max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profiles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
                'ordering': ['tel'],
            },
        ),
    ]
