# Generated by Django 3.2.5 on 2021-08-06 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default='recipes/images/noimage.png', upload_to=''),
        ),
    ]
