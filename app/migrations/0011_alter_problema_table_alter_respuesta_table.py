# Generated by Django 5.0.2 on 2024-10-16 03:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_lventau_alter_problema_options_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='problema',
            table='problema',
        ),
        migrations.AlterModelTable(
            name='respuesta',
            table='respuesta',
        ),
    ]