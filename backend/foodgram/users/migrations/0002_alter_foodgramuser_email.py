# Generated by Django 3.2.5 on 2021-07-12 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodgramuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
