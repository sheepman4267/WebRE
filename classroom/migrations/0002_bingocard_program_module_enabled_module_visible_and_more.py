# Generated by Django 4.0.2 on 2022-02-20 19:13

import colorfield.fields
import datetime
from django.db import migrations, models
import django.db.models.deletion
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BingoCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('publish_date', models.DateField(default=datetime.date.today, editable=False, verbose_name='date published')),
                ('updated_date', models.DateField(default=datetime.date.today, editable=False, verbose_name='date updated')),
                ('body', markdownx.models.MarkdownxField()),
                ('accent_color', colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=18, samples=None)),
                ('page', models.IntegerField(unique=True)),
                ('body_markdown', models.TextField(null=True)),
                ('columns', models.IntegerField()),
                ('rows', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('body', markdownx.models.MarkdownxField()),
                ('background_color', colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=18, samples=None)),
                ('enabled', models.BooleanField(default=False)),
                ('visible', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='module',
            name='enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='module',
            name='visible',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='participant_posts_allowed',
            field=models.BooleanField(default=True, verbose_name='Allow Participant Posts'),
        ),
        migrations.AlterField(
            model_name='module',
            name='body',
            field=markdownx.models.MarkdownxField(blank=True),
        ),
        migrations.CreateModel(
            name='BingoCardItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', markdownx.models.MarkdownxField(null=True)),
                ('body_markdown', models.TextField(null=True)),
                ('pos_x', models.IntegerField()),
                ('pos_y', models.IntegerField()),
                ('sequence', models.IntegerField(null=True)),
                ('visible', models.BooleanField(default=True)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='classroom.bingocard')),
            ],
            options={
                'ordering': ['sequence'],
            },
        ),
        migrations.AddField(
            model_name='bingocard',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classroom.module'),
        ),
        migrations.AddField(
            model_name='module',
            name='program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='classroom.program'),
        ),
        migrations.AddField(
            model_name='profile',
            name='enrollment',
            field=models.ManyToManyField(related_name='participants', to='classroom.Program'),
        ),
    ]