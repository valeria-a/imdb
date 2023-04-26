import django_filters
from django.db import transaction
from django_filters.rest_framework import FilterSet
from rest_framework import viewsets, mixins
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission, SAFE_METHODS
from rest_framework.viewsets import GenericViewSet

from imdb_app.models import Movie
from imdb_app.serializers.movies import MovieSerializer


class MoviesPaginationClass(PageNumberPagination):
    page_size = 5


class MoviesPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH']:
            return request.user.is_staff
        if request.method == 'DELETE':
            return request.user.is_superuser
        return True

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user


class MovieFilterSet(FilterSet):

    name = django_filters.CharFilter(field_name='name', lookup_expr='iexact')
    release_year_min = django_filters.NumberFilter('release_year', lookup_expr='gte')
    release_year_max = django_filters.NumberFilter('release_year', lookup_expr='lte')
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains')

    class Meta:
        model = Movie
        fields = ['name']

class MoviesViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):

    queryset = Movie.objects.all()

    permission_classes = [MoviesPermissions]

    # we need different serializers for different actions
    serializer_class = MovieSerializer

    # pagination is defined either using DEFAULT_PAGINATION_CLASS in settings.py
    # or you can specify one here
    pagination_class = MoviesPaginationClass

    filterset_class = MovieFilterSet

    def perform_create(self, serializer):
        # inject created_by user
        # important to execute everything in one single transaction
        with transaction.atomic():
            super().perform_create(serializer)
            serializer.instance.created_by = self.request.user
            serializer.instance.save()

