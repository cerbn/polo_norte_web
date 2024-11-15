# Generated by Django 5.0.2 on 2024-10-16 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_comentarios_usuarios_problema_respuesta_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LVentaU',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('isbn', models.FloatField(blank=True, null=True)),
                ('titulo', models.CharField(blank=True, max_length=255, null=True)),
                ('precio', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('stock', models.FloatField(blank=True, null=True)),
                ('estado', models.CharField(blank=True, max_length=25, null=True)),
                ('descripcion', models.CharField(blank=True, max_length=4000, null=True)),
                ('solicitud', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'db_table': 'l_venta_u',
                'managed': False,
            },
        ),
        migrations.AlterModelOptions(
            name='problema',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='respuesta',
            options={'managed': False},
        ),
    ]
