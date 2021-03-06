# Generated by Django 4.0.5 on 2022-06-26 11:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('swoosh_app', '0014_alter_brand_id_alter_category_id_alter_order_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdetails',
            name='product_id',
        ),
        migrations.RemoveField(
            model_name='product',
            name='quantity',
        ),
        migrations.CreateModel(
            name='ProductDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(null=True)),
                ('product_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='swoosh_app.product')),
                ('size_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='swoosh_app.size')),
            ],
        ),
        migrations.AddField(
            model_name='orderdetails',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='swoosh_app.productdetail'),
        ),
    ]
