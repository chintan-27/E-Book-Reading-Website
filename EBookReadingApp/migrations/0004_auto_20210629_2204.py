# Generated by Django 3.0.6 on 2021-06-29 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EBookReadingApp', '0003_auto_20210626_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.FloatField(),
        ),
    ]
