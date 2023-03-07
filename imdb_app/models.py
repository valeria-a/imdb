from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):

    class Meta:
        db_table = 'movies'
        ordering = ['id']

    name = models.CharField(max_length=256, db_column='name', null=False, blank=False)
    description = models.TextField(db_column='description', null=True, blank=True)
    release_year = models.IntegerField(db_column='release_year', null=False, blank=False)
    poster_url = models.URLField(max_length=512, db_column='poster_url', null=True, blank=True)

    def __str__(self):
        return self.name


class Review(models.Model):

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.SmallIntegerField(
        db_column='rating', null=False, validators=[MinValueValidator(1), MaxValueValidator(10)])
    review_text = models.TextField(
        db_column='review_text', null=True, blank=True
    )

    created_at = models.DateField(db_column='created_at', null=False, auto_now_add=True)

    class Meta:
        db_table = 'reviews'

