# Generated by Django 2.0.9 on 2024-05-03 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20240503_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='changedisub',
            name='notified',
            field=models.BooleanField(default=False),
        ),
    ]