# Generated by Django 2.0.2 on 2018-05-26 07:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('birddb', '0003_auto_20180526_0745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bird',
            name='web_data',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='birddb.WebData'),
        ),
    ]