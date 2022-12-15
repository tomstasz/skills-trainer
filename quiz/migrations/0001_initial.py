# Generated by Django 4.0.8 on 2022-12-15 08:47

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('company', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prog_language', models.CharField(choices=[('Java', 'Java'), ('Python', 'Python'), ('PHP', 'PHP'), ('C++', 'C++')], max_length=64, verbose_name='Programming Language')),
                ('seniority', models.IntegerField(choices=[(1, 'junior'), (2, 'regular'), (3, 'senior')], verbose_name='Seniority')),
                ('user_name', models.CharField(max_length=120, verbose_name='User Name')),
                ('email', models.CharField(max_length=120, unique=True)),
                ('number_of_questions', models.IntegerField(choices=[(6, 6), (9, 9), (12, 12)], verbose_name='Number of questions')),
                ('general_score', models.IntegerField(default=0)),
                ('junior_score', models.IntegerField(default=0)),
                ('regular_score', models.IntegerField(default=0)),
                ('senior_score', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(blank=True, max_length=240, null=True)),
                ('text_en', models.CharField(blank=True, max_length=240, null=True)),
                ('text_pl', models.CharField(blank=True, max_length=240, null=True)),
                ('question_type', models.CharField(choices=[('multiple choice', 'multiple choice'), ('open', 'open'), ('true/false', 'true/false'), ('image', 'image')], max_length=64)),
                ('prog_language', models.CharField(choices=[('Java', 'Java'), ('Python', 'Python'), ('PHP', 'PHP'), ('C++', 'C++')], max_length=64, verbose_name='Programming Language')),
                ('seniority', models.IntegerField(choices=[(1, 'junior'), (2, 'regular'), (3, 'senior')], db_index=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='../static/images')),
                ('time', models.IntegerField(default=30)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz.author')),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(blank=True, max_length=240, null=True)),
                ('text_en', models.CharField(blank=True, max_length=240, null=True)),
                ('text_pl', models.CharField(blank=True, max_length=240, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='../static/images')),
                ('is_correct', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.question')),
            ],
        ),
    ]
