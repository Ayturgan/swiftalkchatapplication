# Generated by Django 4.2.5 on 2023-10-03 16:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_customuser_email'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='phone',
            new_name='full_phone',
        ),
    ]
