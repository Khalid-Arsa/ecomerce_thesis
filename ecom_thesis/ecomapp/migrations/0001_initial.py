# Generated by Django 3.2.4 on 2021-06-23 18:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('category', models.CharField(choices=[('M', 'Mobile'), ('A', 'Accessories')], max_length=2)),
                ('image', models.ImageField(upload_to='products')),
                ('marked_price', models.PositiveIntegerField()),
                ('selling_price', models.PositiveIntegerField()),
                ('description', models.TextField()),
                ('brand', models.CharField(choices=[('Samsung', 'Samsung'), ('Apple', 'Apple'), ('Huawei', 'Huawei'), ('Nokia', 'Nokia'), ('Lenovo', 'Lenovo'), ('Oppo', 'Oppo'), ('Vivo', 'Vivo'), ('CherryMobile', 'CherryMobile'), ('Xiaomi', 'Xiaomi'), ('LG', 'LG')], max_length=20)),
                ('view_count', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/images/')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecomapp.product')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=200)),
                ('barangay', models.CharField(blank=True, max_length=200, null=True)),
                ('street', models.CharField(blank=True, max_length=200, null=True)),
                ('city', models.CharField(blank=True, max_length=200, null=True)),
                ('province', models.CharField(blank=True, max_length=200, null=True)),
                ('postal', models.IntegerField(blank=True, null=True)),
                ('mobile', models.CharField(max_length=11)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('subtotal', models.PositiveIntegerField()),
                ('discount', models.PositiveIntegerField()),
                ('total', models.PositiveIntegerField()),
                ('order_status', models.CharField(choices=[('Order Received', 'Order Received'), ('Order Pending', 'Order Pending'), ('Order Processing', 'Order Processing'), ('Order Completed', 'Order Completed'), ('Order Canceled', 'Order Canceled')], max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment_method', models.CharField(choices=[('Remittance', 'Remittance'), ('Gcash', 'Gcash')], default='Remittance', max_length=20)),
                ('payment_completed', models.BooleanField(blank=True, default=False, null=True)),
                ('number', models.CharField(max_length=20)),
                ('cart', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ecomapp.cart')),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('mobile', models.CharField(max_length=11)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=50)),
                ('joined_on', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.PositiveIntegerField()),
                ('quantity', models.PositiveIntegerField()),
                ('subtotal', models.PositiveIntegerField()),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecomapp.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecomapp.product')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ecomapp.customer'),
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=50)),
                ('image', models.ImageField(upload_to='admins')),
                ('mobile', models.CharField(max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
