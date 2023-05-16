from django.db import models
from .favoriterestaurant import FavoriteRestaurant
from django.contrib.auth.models import User

class Restaurant(models.Model):
    """Restaurant Model"""
    name = models.CharField(max_length=55, unique=True)
    address = models.CharField(max_length=255)
    # [x]: establish a many-to-many relationship with User through the join model
    favoriters = models.ManyToManyField(User, through=FavoriteRestaurant, related_name='favorited_restaurants')
    # [x]: Add a `is_favorite` custom property. Remember each JSON representation of a restaurant should have a `is_favorite` property. Not just the ones where the value is `true`.
    @property
    def is_favorite(self):
        return self.__is_favorite

    @is_favorite.setter
    def is_favorite(self, value):
        self.__is_favorite = value
