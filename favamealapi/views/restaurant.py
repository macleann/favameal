"""View module for handling requests about restaurants"""
from rest_framework.exceptions import ValidationError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from favamealapi.models import Restaurant
from django.contrib.auth.models import User

class RestaurantSerializer(serializers.ModelSerializer):
    """JSON serializer for restaurants"""

    class Meta:
        model = Restaurant
        # [x]: Add 'is_favorite' field to RestaurantSerializer
        fields = ('id', 'name', 'address', 'is_favorite')


class RestaurantView(ViewSet):
    """ViewSet for handling restuarant requests"""

    def create(self, request):
        """Handle POST operations for restaurants

        Returns:
            Response -- JSON serialized event instance
        """
        try:
            rest = Restaurant.objects.create(
                name=request.data['name'],
                address=request.data["address"]
            )
            serializer = RestaurantSerializer(rest)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single event

        Returns:
            Response -- JSON serialized game instance
        """
        try:
            restaurant = Restaurant.objects.get(pk=pk)
            current_user = User.objects.get(pk=request.auth.user_id)
            # [x]: Add the correct value to the `is_favorite` property of the requested restaurant
            # Hint -- remember the 'many to many field' for referencing the records of users who have favorited this restaurant
            restaurant.is_favorite = current_user in restaurant.favoriters.all()
            serializer = RestaurantSerializer(restaurant)
            return Response(serializer.data)
        except Restaurant.DoesNotExist as ex:
            return Response({"reason": ex.message}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests to restaurants resource

        Returns:
            Response -- JSON serialized list of restaurants
        """
        restaurants = Restaurant.objects.all()
        current_user = User.objects.get(pk=request.auth.user_id)
        # [x]: Add the correct value to the `is_favorite` property of each restaurant
        # Hint -- Iterate over restaurants and look at each one's collection of favorites.
        # Remember the 'many to many field' for referencing the records of users who have favorited this restaurant
        for restaurant in restaurants:
            restaurant.is_favorite = current_user in restaurant.favoriters.all()
        serializer = RestaurantSerializer(restaurants, many=True)

        return Response(serializer.data)

    # [x]: Write a custom action named `favorite` that will allow a client to
    # send a POST request to /restaurant/2/favorite and add the restaurant as a favorite
    @action(methods=['POST'], detail=True)
    def favorite(self, request, pk):
        """Handle POST requests to add a given restaurant to current users list of favorite restaurants

        Returns:
            Response -- Confirmation message and 201 CREATED code
        """
        current_user = User.objects.get(pk=request.auth.user_id)
        restaurant = Restaurant.objects.get(pk=pk)
        restaurant.favoriters.add(current_user)
        return Response({'message': 'User added'}, status=status.HTTP_201_CREATED)

    # [x]: Write a custom action named `unfavorite` that will allow a client to
    # send a POST request to /restaurant/2/unfavorite and remove the restaurant as a favorite
    @action(methods=['DELETE'], detail=True)
    def unfavorite(self, request, pk):
        """Handle DELETE requests to remove the current user from the list of restaurant favoriters

        Returns:
            Response -- 204 NO CONTENT code
        """
        current_user = User.objects.get(pk=request.auth.user_id)
        restaurant = Restaurant.objects.get(pk=pk)
        restaurant.favoriters.remove(current_user)
        return Response(None, status=status.HTTP_204_NO_CONTENT)
