# Generated by Django 2.1.1 on 2018-10-28 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0006_auto_20181028_1741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='master',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='补充合同'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='text',
            field=models.TextField(blank=True, null=True, verbose_name='合同条款摘要'),
        ),
    ]