from rest_framework.routers import DefaultRouter

from imdb_app.views.oscars import OscarsViewSet

# automatically defining urls for MoviesViewSet
router = DefaultRouter(trailing_slash=False)
router.register('', OscarsViewSet)

urlpatterns = router.urls

print(urlpatterns)