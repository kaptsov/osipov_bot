# Generated by Django 4.0.4 on 2022-06-01 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devman', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False, unique=True, verbose_name='Telegram id')),
                ('firstname', models.CharField(blank=True, max_length=50, verbose_name='Имя')),
                ('secondname', models.CharField(blank=True, max_length=50, verbose_name='Фамилия')),
                ('starttime', models.TimeField(verbose_name='Начало рабочего интервала')),
                ('finishtime', models.TimeField(verbose_name='Окончание рабочего интервала')),
            ],
        ),
        migrations.AlterField(
            model_name='student',
            name='firstname',
            field=models.CharField(blank=True, max_length=50, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='student',
            name='id',
            field=models.CharField(max_length=50, primary_key=True, serialize=False, unique=True, verbose_name='Telegram id'),
        ),
        migrations.AlterField(
            model_name='student',
            name='secondname',
            field=models.CharField(blank=True, max_length=50, verbose_name='Фамилия'),
        ),
    ]