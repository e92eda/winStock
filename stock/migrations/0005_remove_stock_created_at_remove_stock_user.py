# Generated by Django 4.1 on 2022-09-05 10:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0004_remove_stock_accounttype_remove_stock_commission_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='stock',
            name='user',
        ),
    ]
