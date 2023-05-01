from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User

from imdb_app import validators


class Movie(models.Model):

    class Meta:
        db_table = 'movies'
        ordering = ['id']

    name = models.CharField(max_length=256, db_column='name', null=False, db_index=True,
                            blank=False)
    description = models.TextField(db_column='description', null=True, blank=True)
    release_year = models.IntegerField(db_column='release_year', null=False, blank=False)
    duration_in_min = models.FloatField(db_column='duration', null=True, blank=True)
    poster_url = models.URLField(max_length=512, db_column='poster_url', null=True, blank=True)

    director = models.ForeignKey('Director', on_delete=models.RESTRICT, null=True)
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT, null=True)

    def __str__(self):
        return self.name


class Review(models.Model):

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.SmallIntegerField(
        db_column='rating', null=False,
        validators=[MinValueValidator(1), MaxValueValidator(10)])
    review_text = models.TextField(
        db_column='review_text', null=True, blank=True
    )

    created_at = models.DateField(db_column='created_at', null=False, auto_now_add=True)

    class Meta:
        db_table = 'reviews'


class Actor(models.Model):

    name = models.CharField(max_length=256, null=False, blank=False)
    birth_year = models.IntegerField(null=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'actors'


class Director(models.Model):

    name = models.CharField(max_length=256, null=False, blank=False)
    birth_year = models.IntegerField(null=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'directors'


class MovieActor(models.Model):
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    salary = models.IntegerField()
    main_role = models.BooleanField(null=False, blank=False)

    def __str__(self):
        return f"{self.actor.name} in movie {self.movie.name}"

    class Meta:
        db_table = 'movie_actors'


class Oscar(models.Model):

    NOMINATIONS = {
        'movie': [
            ('best_picture', 'Best picture'),
            ('international_feature', 'International Feature'),
            ('documentary_short', 'Documentary Short'),
            ('documentary', 'Documentary'),
            ('animated', 'Animated'),
            ('animated_short', 'Animated Short'),
            ('adapted_screenplay', 'Adapted Screenplay'),
            ('original_screenplay', 'Original Screenplay'),
            ('production_design', 'Production Design'),
            ('cinematography', 'Cinematography'),
            ('costume_design', 'Costume Design'),
            ('achievement_in_sound', 'Achievement in sound'),
            ('live_action_short', 'Live Action Short'),
            ('original', 'Original'),
            ('visual_effect', 'Visual Effect'),
            ('film_editing', 'Film Editing'),
            ('makeup_and_hairstyling', 'Makeup and hairstyling'),
        ],
        'actor': [
            ('actress_supporting_role', 'Actress in supporting role'),
            ('actor_supporting_role', 'Actor in supporting role'),
            ('actress_leading_role', 'Actress in leading role'),
            ('actor_leading_role', 'Actor in leading role'),
        ],
        'director': [
            ('director', 'Director')
        ]
    }

    movie = models.ForeignKey(Movie, on_delete=models.RESTRICT, related_name='oscars')
    actor = models.ForeignKey(Actor, null=True, blank=True, on_delete=models.RESTRICT)
    director = models.ForeignKey(Director, null=True, blank=True, on_delete=models.RESTRICT)
    nomination_type = models.CharField(
        max_length=128,
        choices=NOMINATIONS['movie'] + NOMINATIONS['actor'] + NOMINATIONS['director'])
    year = models.IntegerField(
        validators=[MinValueValidator(1929), validators.validate_year_before_now],
        null=True, blank=True
    )

    class Meta:
        db_table = 'oscars'
        ordering = ['id']