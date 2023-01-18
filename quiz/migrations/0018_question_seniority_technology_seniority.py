# Generated by Django 4.0.8 on 2023-01-16 09:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0017_alter_seniority_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='seniority',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='quiz.seniority'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='technology',
            name='seniority',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='quiz.seniority'),
            preserve_default=False,
        ),
    ]