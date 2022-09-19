from django.db import models


# Create your models here.


class Genre(models.Model):
    name = models.CharField(max_length=50, db_index=True, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to='genreimages/')

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return f'/{self.slug}/'


class Style(models.Model):
    name = models.CharField(max_length=50, db_index=True, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to='styleimages/')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}/'


class Artist(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    originalName = models.CharField(max_length=100, blank=True, null=True)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    biography = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(blank=True, null=True, upload_to='artistimages/')
    dateOfBirth = models.DateField()
    dateOfDeath = models.DateField()
    birthDayString = models.CharField(max_length=100, blank=True, null=True)
    deathDayString = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}/'


class Gallery(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(blank=True, null=True, upload_to='galleryimages/')

    class Meta:
        verbose_name_plural = 'galleries'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}/'


class Painting(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='paintings')
    description = models.TextField(blank=True, null=True)
    completionYear = models.IntegerField(null=True)
    sizeX = models.DecimalField(max_digits=10, decimal_places=2)
    sizeY = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, null=True)
    widthImg = models.IntegerField()
    heightImg = models.IntegerField()
    image = models.ImageField(blank=True, null=True, upload_to='paintingimages/')
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='painting_gallery')
    popularityN = models.IntegerField(unique=True)
    genre = models.ManyToManyField(Genre)
    style = models.ManyToManyField(Style)

    class Meta:
        verbose_name_plural = 'paintings'
        ordering = ('popularityN',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/{self.slug}/'


def upload_path(instance,filename):
    return'/'.join(['paintingimages',str(instance.painting), filename])


class ImageModel(models.Model):
    painting = models.CharField(blank=True, null=True, max_length=5000)
    image = models.ImageField(blank=False, null=False, upload_to=upload_path)
