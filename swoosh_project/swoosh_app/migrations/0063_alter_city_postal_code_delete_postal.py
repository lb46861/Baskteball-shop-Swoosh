# Generated by Django 4.0.5 on 2022-08-08 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('swoosh_app', '0062_rename_city_city_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='postal_code',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name='Postal',
        ),
    ]
