# Generated by Django 3.0.4 on 2020-03-27 11:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=8, default=0, max_digits=30)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.Account')),
            ],
            options={
                'db_table': 'account_item',
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('symbol', models.URLField(max_length=500)),
                ('is_active', models.BooleanField(default=False)),
                ('is_base_currency', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'currencies',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('price_unit', models.DecimalField(decimal_places=3, max_digits=8)),
                ('amount_unit', models.DecimalField(decimal_places=3, max_digits=8)),
                ('is_active', models.BooleanField(default=False)),
                ('account', models.ManyToManyField(through='exchange.AccountItem', to='account.Account')),
                ('currency', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='exchange.Currency')),
            ],
            options={
                'db_table': 'items',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opening_price', models.DecimalField(decimal_places=8, max_digits=30)),
                ('high_price', models.DecimalField(decimal_places=8, max_digits=30)),
                ('low_price', models.DecimalField(decimal_places=8, max_digits=30)),
                ('trade_price', models.DecimalField(decimal_places=8, max_digits=30)),
                ('candle_price', models.DecimalField(decimal_places=8, max_digits=30)),
                ('candle_volume', models.DecimalField(decimal_places=8, max_digits=30)),
                ('unit', models.CharField(max_length=50)),
                ('date', models.DateTimeField(max_length=100)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exchange.Currency')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exchange.Item')),
            ],
            options={
                'db_table': 'reports',
            },
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trade_price', models.DecimalField(decimal_places=8, max_digits=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exchange.Currency')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exchange.Item')),
            ],
            options={
                'db_table': 'price',
            },
        ),
        migrations.AddField(
            model_name='accountitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exchange.Item'),
        ),
    ]
