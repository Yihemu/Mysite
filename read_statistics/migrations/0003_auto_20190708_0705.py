# Generated by Django 2.2 on 2019-07-08 07:05

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('read_statistics', '0002_readdetail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='readdetail',
            name='date',
            field=models.DateField(default=datetime.datetime(2019, 7, 8, 7, 5, 19, 802674, tzinfo=utc)),
        ),
    ]
