# Generated by Django 5.0.6 on 2024-05-22 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_alter_customer_telegram_id_alter_orderstatus_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='quantity',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
    ]