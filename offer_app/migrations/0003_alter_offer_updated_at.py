# Generated by Django 5.2.1 on 2025-05-30 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offer_app', '0002_alter_offerdetail_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
