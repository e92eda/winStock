# Generated by Django 4.1 on 2022-09-08 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0011_alter_stock_valuation'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='holding',
            field=models.BooleanField(default=False),
        ),
    ]