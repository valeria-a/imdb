from django.urls import path
from rest_framework.routers import DefaultRouter

from imdb_app.views.movies import MoviesViewSet

# automatically defining urls for MoviesViewSet
router = DefaultRouter()
router.register('', MoviesViewSet)


urlpatterns = []

# adding movies urls to urlpatterns
urlpatterns.extend(router.urls)
