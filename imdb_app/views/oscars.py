import django_filters
from django.db import connection
from django_filters import FilterSet
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from imdb_app import models
from imdb_app.models import Oscar, Movie
from imdb_app.serializers.oscars import OscarSerializer, CreateOscarSerializer, UpdateOscarSerializer


class OscarFilterSet(FilterSet):
    from_year = django_filters.NumberFilter('year', lookup_expr='gte')
    to_year = django_filters.NumberFilter('year', lookup_expr='lte')
    nomination = django_filters.CharFilter('nomination_type')
    actor_nominations = django_filters.BooleanFilter(method='filter_by_actor_nominations')

    def filter_by_actor_nominations(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                nomination_type__in=[n[0] for n in models.Oscar.NOMINATIONS['actor']])
        return queryset

    class Meta:
        model = Oscar
        fields = ['year']


class OscarsViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):

    queryset = models.Oscar.objects.all()
    serializer_class = OscarSerializer
    filterset_class = OscarFilterSet

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateOscarSerializer
        elif self.action == 'update':
            return UpdateOscarSerializer
        else:
            return self.serializer_class

    def filter_queryset(self, queryset):
        if self.action == 'get_oscars_by_year':
            queryset = queryset.filter(year=self.kwargs['year'])
        # will call FilterBackend with FilterSet
        queryset = super().filter_queryset(queryset)
        return queryset

    # api/oscars -> detail=False
    # api/oscars/<oscar_id> -> detail=True
    # api/oscars/years/2003
    # r'years/(\d{4})'
    # years/1999
    # match.group(1)
    @action(methods=['GET'], detail=False, url_path=r'years/(?P<year>\d{4})$')
    def get_oscars_by_year(self, request, year=None):
        # just return the default list logic, specific filtering will be performed in
        # filter_queryset overwrite
        return super().list(request, year=year)

    @action(methods=['GET'], detail=False, url_path=r'stats$')
    def stats(self, request):

        data = {}

        # get total oscars
        data['total_oscars'] = Oscar.objects.all().count()

        with connection.cursor() as cursor:
            cursor.execute("""
            select count(o.movie_id) as oscars_cnt, m.name, m.id 
            from movies m join oscars o 
            on o.movie_id = m.id
            group by m.id, m.name
            order by oscars_cnt desc
            limit 1;""")
            columns = [col[0] for col in cursor.description]
            movie_with_most_oscars = dict(zip(columns, cursor.fetchone()))
            data['movie_with_most_oscars'] = movie_with_most_oscars

            cursor.execute("""
            select count(o.actor_id) as oscars_cnt, a.name, a.id 
            from actors a join oscars o 
            on o.actor_id = a.id
            group by a.id, a.name
            order by oscars_cnt desc
            limit 1;
            """)
            columns = [col[0] for col in cursor.description]
            actor_with_most_oscars = dict(zip(columns, cursor.fetchone()))
            data['actor_with_most_oscars'] = actor_with_most_oscars

        return Response(data)


