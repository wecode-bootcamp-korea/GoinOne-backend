# Generated by Django 3.0.4 on 2020-03-11 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=200, unique=True)),
                ('nickname', models.CharField(max_length=50, null=True)),
                ('bank', models.CharField(max_length=50, null=True)),
                ('bank_account', models.CharField(max_length=200, null=True)),
                ('address', models.CharField(max_length=500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'accounts',
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=8, max_digits=16)),
                ('origin_amount', models.DecimalField(decimal_places=8, max_digits=16)),
                ('remined_amount', models.DecimalField(decimal_places=8, max_digits=16)),
                ('buy', models.BooleanField(default=False)),
                ('sell', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'offers',
            },
        ),
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=8, max_digits=16)),
                ('price_unit', models.DecimalField(decimal_places=8, max_digits=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('buyer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='buyer', to='account.Account')),
            ],
            options={
                'db_table': 'trade',
            },
        ),
    ]
