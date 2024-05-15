# Generated by Django 5.0.4 on 2024-05-14 14:12

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_transaction_wallet'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={'verbose_name_plural': 'واریز پول و پرداخت ها'},
        ),
        migrations.AddField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='wallet',
            field=models.ForeignKey(blank=True, default="", on_delete=django.db.models.deletion.CASCADE, to='store.wallet'),
            preserve_default=False,
        ),
    ]