# Generated by Django 3.1.7 on 2023-12-22 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_favoriteart'),
    ]

    operations = [
        migrations.AddField(
            model_name='artwork',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]
