# Generated by Django 4.0.6 on 2022-09-23 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('territorio', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='foto',
            field=models.ImageField(default='territorio/fotos/default.png', upload_to='territorio/fotos'),
        ),
    ]