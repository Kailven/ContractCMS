# Generated by Django 2.1.1 on 2018-11-05 01:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('requisitions', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='requisition',
            options={'ordering': ('contract', 'created'), 'verbose_name': '请款记录', 'verbose_name_plural': '请款记录'},
        ),
    ]
