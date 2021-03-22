# Generated by Django 3.1.7 on 2021-03-18 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_courier_finished_amount_regions'),
    ]

    operations = [
        migrations.AddField(
            model_name='courier',
            name='earning_coef',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='courier',
            name='total_earning',
            field=models.IntegerField(default=0),
        ),
    ]