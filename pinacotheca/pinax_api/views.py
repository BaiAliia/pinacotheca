from rest_framework import permissions, generics, viewsets, status
from rest_framework.views import APIView

from usersapp.models import UserAccount
from pinax.models import Painting, Genre, Gallery, Artist, Style
from usersapp.models import Comment
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, BasePermission, IsAdminUser, AllowAny

from usersapp.serializers import UserSerializer
from .serializers import PaintingSerializer, GenreSerializer, GallerySerializer, ArtistSerializer, StyleSerializer, \
    CommentSerializer
from rest_framework.response import Response
from .permissions import IsEditorOrReadOnly, IsAuthorOrReadOnly


# Create your views here.


class PaintingViewSet(viewsets.ModelViewSet):
    serializer_class = PaintingSerializer
    queryset = Painting.objects.all()
    permission_classes = (AllowAny,)


class ArtistViewSet(viewsets.ModelViewSet):
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()
    permission_classes = (AllowAny,)


class StyleViewSet(viewsets.ModelViewSet):
    serializer_class = StyleSerializer
    queryset = Style.objects.all()
    permission_classes = (AllowAny,)


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = (AllowAny,)
    serializer = serializer_class(queryset, many=True)
    test1 = serializer.data[0]
    painting = test1.get('painting_set')
    sec = painting[0]
    print(sec)
    print(painting)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = UserAccount.objects.all()
    permission_classes = (AllowAny,)


class GalleryViewSet(viewsets.ModelViewSet):
    serializer_class = GallerySerializer
    queryset = Gallery.objects.all()
    permission_classes = (AllowAny,)


class AddCommentView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = ()

    def post(self, request, painting_id=None):
        painting = Painting.objects.get(pk=painting_id)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(painting=painting, author=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManageCommentsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    lookup_url_kwarg = 'comment_id'
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        queryset = Comment.objects.all()
        return queryset


class FavoriteView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None, painting_id=None):
        painting = Painting.objects.get(pk=painting_id)
        user = self.request.user
        if user.is_authenticated:
            if user in painting.account.all():
                favorite = False
                painting.account.remove(user)
            else:
                favorite = True
                painting.account.add(user)
            data = {
                'favorite': favorite
            }
            return Response(data)


class UserFavoritesView(generics.ListAPIView):
    serializer_class = PaintingSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        favorited_painting = user.favourites.all()
        queryset = Painting.objects.all().filter(pk__in=favorited_painting)
        print(queryset)
        return queryset
