# Generated by Django 2.1.15 on 2020-04-17 05:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_auto_20200417_1355'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookinstance',
            options={'permissions': [('mark_bookinstance', 'can mark book instance')]},
        ),
    ]
