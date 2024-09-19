# Generated by Django 5.1 on 2024-09-14 11:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_remove_order_color_remove_order_link_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='color',
        ),
        migrations.RemoveField(
            model_name='product',
            name='size',
        ),
        migrations.AddField(
            model_name='product',
            name='unit_price',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='قیمت'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='اسم'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='telegram_id',
            field=models.CharField(max_length=100, verbose_name='کد تلگرام'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ'),
        ),
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.customer', verbose_name='مشتری'),
        ),
        migrations.AlterField(
            model_name='order',
            name='description',
            field=models.TextField(help_text='Enter the product description', verbose_name='توضیحات'),
        ),
        migrations.AlterField(
            model_name='order',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product', verbose_name='محصول'),
        ),
        migrations.AlterField(
            model_name='order',
            name='quantity',
            field=models.PositiveSmallIntegerField(verbose_name='تعداد'),
        ),
        migrations.AlterField(
            model_name='orderstatus',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='store.order', verbose_name='سفارش'),
        ),
        migrations.AlterField(
            model_name='orderstatus',
            name='status',
            field=models.CharField(choices=[('P', 'در انتظار'), ('A', 'تایید شده'), ('C', 'پرداخت شده'), ('F', 'لغو شده'), ('S', 'ارسال شده'), ('R', 'دریافت شده')], default='P', max_length=1, verbose_name='وضعیت'),
        ),
        migrations.AlterField(
            model_name='orderstatus',
            name='status_change',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ تغییر'),
        ),
        migrations.AlterField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ'),
        ),
        migrations.AlterField(
            model_name='product',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.customer', verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='product',
            name='is_public',
            field=models.BooleanField(default=False, help_text='Is this a public product?', verbose_name='وضعیت در سایت'),
        ),
        migrations.AlterField(
            model_name='product',
            name='link',
            field=models.URLField(help_text='Enter the product link', verbose_name='لینک'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='مقدار'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='receipts/', verbose_name='رسید'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('C', 'Confirmed'), ('R', 'Rejected')], default='P', max_length=1, verbose_name='وضعیت'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='wallet',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='store.wallet', verbose_name='کیف پول'),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='amount',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='موجودی'),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='customer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='wallet', to='store.customer', verbose_name='مشتری'),
        ),
    ]