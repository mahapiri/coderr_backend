# Generated by Django 5.2.1 on 2025-06-02 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0004_remove_order_offer_detail_order_offer_detail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='in_progress', max_length=255),
        ),
    ]
