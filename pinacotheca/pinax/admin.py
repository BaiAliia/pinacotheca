from django.contrib import admin
from .models import Genre, Style, Artist, Painting, Gallery

admin.site.register(Genre)
admin.site.register(Style)
admin.site.register(Artist)
admin.site.register(Painting)
admin.site.register(Gallery)

# Register your models here.
