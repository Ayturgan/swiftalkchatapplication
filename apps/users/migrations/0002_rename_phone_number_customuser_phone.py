# Generated by Django 4.2.5 on 2023-10-03 13:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='phone_number',
            new_name='phone',
        ),
    ]