# Generated by Django 4.0.8 on 2023-02-10 12:01

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0024_alter_quiz_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
