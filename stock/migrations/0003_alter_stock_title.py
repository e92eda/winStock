# Generated by Django 4.2.7 on 2023-11-06 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0002_alter_stock_symboldisp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='title',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='タイトル'),
        ),
    ]
