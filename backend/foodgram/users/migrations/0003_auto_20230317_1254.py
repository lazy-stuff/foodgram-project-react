# Generated by Django 2.2.16 on 2023-03-17 12:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20230317_1147'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ('-id',), 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
    ]
