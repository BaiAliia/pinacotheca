from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaintingViewSet, ArtistViewSet, StyleViewSet, GenreViewSet, GalleryViewSet, UserViewSet, \
    AddCommentView, ManageCommentsView, UserFavoritesView, FavoriteView, ImageViewSet

app_name = 'pinax_api'

router = DefaultRouter()
router.register(r'painting', PaintingViewSet, basename='painting')
router.register(r'artist', ArtistViewSet, basename='artist')
router.register(r'genre', GenreViewSet, basename='genre')
router.register(r'gallery', GalleryViewSet, basename='gallery')
router.register(r'style', StyleViewSet, basename='style')
router.register(r'users', UserViewSet, basename='user')
router.register(r'image', ImageViewSet, basename='image')


urlpatterns =[
    path('add-comment/<int:painting_id>/', AddCommentView.as_view(), name='add-comment'),
    path('comment/<int:comment_id>/', ManageCommentsView.as_view(), name='manage-comment'),
    path('favourites/', UserFavoritesView.as_view(), name='favorites'),
    path('favorite/<int:painting_id>/', FavoriteView.as_view(), name='favorite'),
    path('auth/', include('usersapp.urls', namespace='usersapp')),

    path('', include(router.urls)),


]
