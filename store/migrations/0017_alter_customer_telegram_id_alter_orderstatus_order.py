# Generated by Django 5.0.6 on 2024-05-22 16:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_alter_orderinvoice_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='telegram_id',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='orderstatus',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='store.order'),
        ),
    ]
