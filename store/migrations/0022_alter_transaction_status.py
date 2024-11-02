# Generated by Django 4.2.16 on 2024-09-24 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0021_alter_order_options_remove_order_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('P', 'در انتظار تایید'), ('C', 'تایید شده'), ('R', 'رد شده')], default='P', max_length=1, verbose_name='وضعیت'),
        ),
    ]
