from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from imdb_app import models


class OscarActorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Actor
        fields = ['id', 'name']


class OscarDirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Director
        fields = ['id', 'name']

class OscarMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Movie
        fields = ['id', 'name']

class OscarSerializer(serializers.ModelSerializer):

    movie = OscarMovieSerializer()
    director = OscarDirectorSerializer()
    actor = OscarActorSerializer()

    class Meta:
        model = models.Oscar
        fields = '__all__'


class CreateOscarSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Oscar
        fields = ['year', 'nomination_type', 'movie', 'actor', 'director']

    def validate(self, attrs):
        actor_nominations = (n[0] for n in models.Oscar.NOMINATIONS['actor'])
        if attrs['nomination_type'] in actor_nominations and not attrs.get('actor'):
            raise ValidationError(detail='Actor is not provided for actor-related nomination')

        director_nominations = (n[0] for n in models.Oscar.NOMINATIONS['director'])
        if attrs['nomination_type'] in director_nominations and not attrs.get('director'):
            raise ValidationError(detail='Director is not provided for director-related nomination')
        return attrs


class UpdateOscarSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Oscar
        fields = ['actor', 'movie', 'director']

    def validate(self, attrs):

        # actor provided for non-actor nominations
        actor_nominations = (n[0] for n in models.Oscar.NOMINATIONS['actor'])
        if attrs.get('actor') and self.instance.nomination_type not in actor_nominations:
            raise ValidationError(detail='Actor provided for non actor-related nomination')

        # director provided for non-director nomination
        director_nominations = (n[0] for n in models.Oscar.NOMINATIONS['director'])
        if attrs.get('director') and self.instance.nomination_type not in director_nominations:
            raise ValidationError(detail='Director provided for non director-related nomination')

        return attrs