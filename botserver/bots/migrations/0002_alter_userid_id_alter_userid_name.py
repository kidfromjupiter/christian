# Generated by Django 5.0.4 on 2024-06-15 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userid',
            name='id',
            field=models.CharField(max_length=255, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='userid',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
