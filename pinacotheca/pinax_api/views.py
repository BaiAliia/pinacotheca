
from rest_framework import generics, viewsets
from usersapp.models import UserAccount
from pinax.models import Painting, Genre, Gallery, Artist, Style
from rest_framework.permissions import  IsAuthenticated, IsAuthenticatedOrReadOnly, BasePermission, IsAdminUser, AllowAny
from .serializers import PaintingSerializer, GenreSerializer, GallerySerializer, ArtistSerializer, StyleSerializer, UserAccountSerializer
from rest_framework import viewsets
from .permissions import IsEditorOrReadOnly
# Create your views here.


class PaintingViewSet(viewsets.ModelViewSet):
    serializer_class = PaintingSerializer
    queryset = Painting.objects.all()
    permission_classes = (AllowAny, )


class ArtistViewSet(viewsets.ModelViewSet):
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()
    permission_classes = (AllowAny, )


class StyleViewSet(viewsets.ModelViewSet):
    serializer_class = StyleSerializer
    queryset = Style.objects.all()
    permission_classes = (AllowAny, )


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = (AllowAny, )
    serializer = serializer_class(queryset, many=True)
    test1 = serializer.data[0]
    painting = test1.get('painting_set')
    sec = painting[0]
    print(sec)
    print(painting)


class GalleryViewSet(viewsets.ModelViewSet):
    serializer_class = GallerySerializer
    queryset = Gallery.objects.all()
    permission_classes = (AllowAny, )