# Generated by Django 4.0.8 on 2023-01-16 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0015_alter_score_quiz_alter_score_technology'),
    ]

    operations = [
        migrations.CreateModel(
            name='Seniority',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(choices=[(1, 'junior'), (2, 'regular'), (3, 'senior')], verbose_name='Seniority')),
            ],
        ),
        migrations.RemoveField(
            model_name='question',
            name='seniority',
        ),
        migrations.RemoveField(
            model_name='quiz',
            name='seniority',
        ),
    ]
