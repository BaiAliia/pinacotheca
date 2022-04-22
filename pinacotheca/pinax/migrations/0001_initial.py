# Generated by Django 3.1 on 2022-04-22 18:00

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('originalName', models.CharField(blank=True, max_length=100, null=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1)),
                ('biography', models.TextField(blank=True, null=True)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='artistimages/')),
                ('dateOfBirth', models.DateField()),
                ('dateOfDeath', models.DateField()),
                ('birthDayString', models.CharField(blank=True, max_length=100, null=True)),
                ('deathDayString', models.CharField(blank=True, max_length=100, null=True)),
                ('country', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('slug', models.SlugField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name_plural': 'galleries',
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=50, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='genreimages/')),
            ],
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=50, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Painting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('artistName', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('completionYear', models.IntegerField(null=True)),
                ('sizeX', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sizeY', models.DecimalField(decimal_places=2, max_digits=10)),
                ('type', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, size=10)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('widthImg', models.IntegerField()),
                ('heightImg', models.IntegerField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='paintingimages/')),
                ('galleryName', models.CharField(blank=True, max_length=255, null=True)),
                ('popularityN', models.IntegerField(unique=True)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='painting', to='pinax.artist')),
                ('gallery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='painting_gallery', to='pinax.gallery')),
                ('genre', models.ManyToManyField(to='pinax.Genre')),
                ('style', models.ManyToManyField(to='pinax.Style')),
            ],
            options={
                'verbose_name_plural': 'paintings',
                'ordering': ('popularityN',),
            },
        ),
    ]