from asyncio.windows_events import NULL
from http.client import HTTPResponse
from django.http import JsonResponse
import asyncio, time
from rest_framework import permissions, generics, viewsets, status
from rest_framework.views import APIView, View
from asgiref.sync import sync_to_async
from usersapp.models import UserAccount
from pinax.models import Painting, Genre, Gallery, Artist, Style,ImageModel
from usersapp.models import Comment
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, BasePermission, IsAdminUser, AllowAny
from django.http import HttpResponse
from usersapp.serializers import UserSerializer
from .serializers import PaintingSerializer, GenreSerializer, GallerySerializer, ArtistSerializer, StyleSerializer, \
    CommentSerializer, ImageUploadSerializer
from rest_framework.response import Response
from .permissions import IsEditorOrReadOnly, IsAuthorOrReadOnly
from .forms import ImageForm
from rest_framework.decorators import api_view

# This Libs are for Result Function
from django.shortcuts import render
import numpy as np
import torchvision
from torchvision import transforms
import torch
import urllib.parse
from PIL import Image as im
import pandas as pd
import sqlalchemy as db
## end of libs for result function

# Create your views here.

from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage


def result (user_img):
    
    hey = 'ajbjnahey'
    print(hey)

    #connecting to azure sql database
    server = "pinacotheca-srv.database.windows.net"
    database = "pinacotheca_db"
    username = "pinacotheca-admin"
    password = "!Pina1234"

    driver = '{ODBC Driver 18 for SQL Server}'
    odbc_str = 'DRIVER='+driver+';SERVER='+server+';PORT=1433;UID='+username+';DATABASE='+ database + ';PWD='+ password
    connect_str = 'mssql+pyodbc:///?odbc_connect=' + urllib.parse.quote_plus(odbc_str)

    cnn_sql = db.create_engine(connect_str)

    #assigning table to DataFrame with original connection
    sql = "SELECT * FROM dbo.paintings;"
    df = pd.read_sql(sql, cnn_sql)

    #Setting model to get features of the image
    model = torchvision.models.vgg16(pretrained=True)
    model1 = model.features
    model2 = model.avgpool
    model3 = model.classifier[:-1]
    model1.eval()
    model2.eval()
    model3.eval()

    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # this is an image read by PIL.Image.open
    user_img = im.open(user_img)
    user_img = preprocess(user_img)
    user_img.unsqueeze(0)
    user_img_feat =  model3(torch.flatten(model2(model1(user_img)))).detach().numpy()

    """ compare input image vector with all db vectors"""
    db_guids = []
    db_feats = []
    for i in range(len(df)):
        db_feat = df.iloc[i, 10]
        db_feat = list(map(float,db_feat.split(",")))
        db_feats.append(db_feat)
        db_guid = df.iloc[i, 9]
        db_guids.append(db_guid)
        
        
    similarities = []
    for db_feat in db_feats:
        #db_feat = np.array(db_feat)
        similarity = 1 - np.linalg.norm(user_img_feat - db_feat)
        similarities.append(similarity)

    most_similar_index = np.argmax(similarities)
    theGuid = db_guids[most_similar_index]
    the_description = df.iloc[most_similar_index, 7]
    the_tags = df.iloc[most_similar_index, 6]
    the_galleries = df.iloc[most_similar_index, 5]
    the_styles = df.iloc[most_similar_index, 4]
    the_completitionyear = df.iloc[most_similar_index, 3]
    the_artistname = df.iloc[most_similar_index, 2]
    the_paintings_title = df.iloc[most_similar_index, 0]

    result = {
        'GUID' : theGuid,
        'DESCRIPTION': the_description,
        'TAGS' : the_tags,
        'GALLERIES' : the_galleries,
        'STYLES' : the_styles,
        'COMPLETITION YEAR' : the_completitionyear,
        'ARTIST NAME' : the_artistname,
        'PAINTINGS TITLE' : the_paintings_title,
    }

    return result

res = NULL





class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageUploadSerializer
    permission_classes =(AllowAny,)
    queryset = ImageModel.objects.all()

    def create(self, request,*args, **kwargs):

        serializer = ImageUploadSerializer(data=request.data)
        image = request.data['image']
        # result (image)
        res=result(image)
        painting = res.get('GUID')
        ImageModel.objects.create(image=image,painting=painting)
            
        if res is not None:
        
            return Response(res,status=status.HTTP_201_CREATED)
      
        else:
            return Response(
                {"Error": "Could not match with the painting from the database"}, status=status.HTTP_400_BAD_REQUEST)


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
    

  #  print(sec)
  #  print(painting)


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
