# Generated by Django 2.2.7 on 2020-04-21 09:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('requisitions', '0002_auto_20181105_0937'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='requisition',
            options={'ordering': ('payday',), 'verbose_name': '请款记录', 'verbose_name_plural': '请款记录'},
        ),
    ]
