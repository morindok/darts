# Generated by Django 3.1.7 on 2023-12-20 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20231220_0551'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='digital_wallet_address',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]