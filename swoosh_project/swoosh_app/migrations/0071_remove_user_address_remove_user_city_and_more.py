# Generated by Django 4.0.5 on 2022-08-09 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swoosh_app', '0070_alter_city_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='address',
        ),
        migrations.RemoveField(
            model_name='user',
            name='city',
        ),
        migrations.RemoveField(
            model_name='user',
            name='country',
        ),
        migrations.RemoveField(
            model_name='user',
            name='postal_code',
        ),
    ]
