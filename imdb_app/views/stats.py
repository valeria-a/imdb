from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from imdb_app.models import Movie, Review


# Create your views here.
@api_view(['GET'])
def stats(request):
    total_movies = Movie.objects.count()
    total_users = User.objects.count()
    total_reviews = Review.objects.count()

    ret_val = {
        'total_movies': total_movies,
        'total_users': total_users,
        'total_reviews': total_reviews
    }
    return Response(ret_val)