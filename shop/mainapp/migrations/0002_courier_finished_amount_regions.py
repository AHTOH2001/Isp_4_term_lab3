# Generated by Django 3.1.7 on 2021-03-18 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='courier',
            name='finished_amount_regions',
            field=models.JSONField(null=True, verbose_name='Количество завершенных заказов по району'),
        ),
    ]
