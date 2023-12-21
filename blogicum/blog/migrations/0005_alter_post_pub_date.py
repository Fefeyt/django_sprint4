# Generated by Django 3.2.16 on 2023-12-21 06:27

import blog.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20231217_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(help_text='Если установить дату и время в будущем — можно делать отложенные публикации.', validators=[blog.validators.real_time], verbose_name='Дата и время публикации'),
        ),
    ]