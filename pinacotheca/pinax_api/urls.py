from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaintingViewSet, ArtistViewSet, StyleViewSet, GenreViewSet, GalleryViewSet

app_name = 'pinax_api'

router = DefaultRouter()
router.register(r'painting', PaintingViewSet, basename='painting')
router.register(r'artist', ArtistViewSet, basename='artist')
router.register(r'genre', GenreViewSet, basename='genre')
router.register(r'gallery', GalleryViewSet, basename='gallery')
router.register(r'style', StyleViewSet, basename='style')

urlpatterns =[
    path('', include(router.urls)),

]