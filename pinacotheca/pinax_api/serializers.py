from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils.datetime_safe import time
from rest_framework import serializers
from pinax.models import Painting, Artist, Gallery, Genre, Style
from usersapp.models import UserAccount, Comment
from django.contrib.postgres.fields import ArrayField


class CommentAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('user_name',)


class CommentSerializer(serializers.ModelSerializer):
    author = CommentAuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('painting', 'author', 'body', 'date_added')
        read_only_fields = ('author', 'painting', 'date_added')


class GenreSerializer(serializers.ModelSerializer):
    num_paintings = serializers.IntegerField(source='painting_set.count', read_only=True)

    class Meta:
        fields = ('id', 'name', 'description', 'slug', 'image', 'num_paintings', 'painting_set')
        model = Genre

    depth = 0


class StyleSerializer(serializers.ModelSerializer):
    num_paintings = serializers.IntegerField(source='painting_set.count', read_only=True)

    class Meta:
        fields = ('id', 'name', 'description', 'slug', 'num_paintings', 'painting_set')
        model = Style


class PaintingSerializer(serializers.ModelSerializer):
    num_favourites = serializers.IntegerField(source='account.count', read_only=True)
    painting_comments = serializers.SerializerMethodField(
        'paginated_comments')
    favorite_by_user = serializers.SerializerMethodField()
    artist_name = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='name',
        source='artist'
    )
    artist_url = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='pinax_api:artist-detail',
        source='artist'
    )
    artist = serializers.PrimaryKeyRelatedField(read_only='True')
    gallery_name = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='name',
        source='gallery'
    )
    gallery_url = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name='pinax_api:gallery-detail',
        source='gallery'
    )
    gallery = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Painting
        fields = (
        'id', 'title', 'slug', 'artist', 'artist_name', 'artist_url', 'description', 'completionYear', 'sizeX', 'sizeY',
        'type', 'location', 'widthImg', 'heightImg', 'image', 'gallery', 'gallery_name', 'gallery_url', 'popularityN',
        'genre',
        'style', 'num_favourites', 'painting_comments', 'favorite_by_user')
        depth = 0

    def get_favorite_by_user(self, obj):
        user = self.context['request'].user
        return user in obj.account.all()

    def paginated_comments(self, obj):
        page_size = 5
        paginator = Paginator(obj.comment.all(), page_size)
        page = self.context['request'].query_params.get('page') or 1

        comment = paginator.page(page)
        serializer = CommentSerializer(comment, many=True)

        return serializer.data


class GallerySerializer(serializers.ModelSerializer):
    num_paintings = serializers.IntegerField(source='painting_gallery.count', read_only=True)

    class Meta:
        fields = ('id', 'name', 'description', 'slug', 'location', 'painting_gallery', 'num_paintings')
        model = Gallery
        depth = 1


class ArtistSerializer(serializers.ModelSerializer):
    num_paintings = serializers.IntegerField(source='paintings.count', read_only=True)

    def validate(self, data):
        if data['dateOfBirth'] > data['dateOfDeath']:
            raise serializers.ValidationError("date of death must occure after the date of birth")
        return data

    class Meta:
        fields = ('id', 'name', 'originalName', 'gender', 'biography', 'slug', 'image',
                  'dateOfBirth', 'dateOfDeath', 'birthDayString', 'deathDayString', 'country', 'paintings',
                  'num_paintings')
        model = Artist
        depth = 1


