"""View module for handling requests about meals"""
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from favamealapi.models import Meal, MealRating, Restaurant, FavoriteMeal
from favamealapi.views.restaurant import RestaurantSerializer
from django.contrib.auth.models import User
from django.db.models import Avg


class MealSerializer(serializers.ModelSerializer):
    """JSON serializer for meals"""
    restaurant = RestaurantSerializer(many=False)

    class Meta:
        model = Meal
        # [x]: Add 'user_rating', 'avg_rating', 'is_favorite' fields to MealSerializer
        fields = ('id', 'name', 'restaurant', 'is_favorite', 'user_rating', 'avg_rating')



class MealView(ViewSet):
    """ViewSet for handling meal requests"""

    def create(self, request):
        """Handle POST operations for meals

        Returns:
            Response -- JSON serialized meal instance
        """
        try:
            meal = Meal.objects.create(
                name=request.data["name"],
                restaurant=Restaurant.objects.get(
                    pk=request.data["restaurant_id"])
            )
            serializer = MealSerializer(meal)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single meal

        Returns:
            Response -- JSON serialized meal instance
        """
        try:
            meal = Meal.objects.get(pk=pk)
            current_user = User.objects.get(pk=request.auth.user_id)
            # [x]: Get the rating for current user and assign to `user_rating` property
            user_rating = MealRating.objects.filter(user=current_user, meal=meal).first()
            meal.user_rating = user_rating.rating if user_rating else 0
            # [x]: Get the average rating for requested meal and assign to `avg_rating` property
            avg_rating = MealRating.objects.filter(meal=meal).aggregate(Avg('rating'))
            meal.avg_rating = avg_rating['rating__avg'] if avg_rating['rating__avg'] is not None else 0
            # [x]: Assign a value to the `is_favorite` property of requested meal
            meal.is_favorite = current_user in meal.frequent_eaters.all()
            serializer = MealSerializer(meal)
            return Response(serializer.data)
        except Meal.DoesNotExist as ex:
            return Response({"reason": ex.message}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests to meals resource

        Returns:
            Response -- JSON serialized list of meals
        """
        meals = Meal.objects.all()
        current_user = User.objects.get(pk=request.auth.user_id)
        for meal in meals:
            # [x]: Get the rating for current user and assign to `user_rating` property
            user_rating = MealRating.objects.filter(user=current_user, meal=meal).first()
            meal.user_rating = user_rating.rating if user_rating else 0
            # [x]: Get the average rating for each meal and assign to `avg_rating` property
            avg_rating = MealRating.objects.filter(meal=meal).aggregate(Avg('rating'))
            meal.avg_rating = avg_rating['rating__avg'] if avg_rating['rating__avg'] is not None else 0
            # [x]: Assign a value to the `is_favorite` property of each meal
            meal.is_favorite = current_user in meal.frequent_eaters.all()
        serializer = MealSerializer(meals, many=True)

        return Response(serializer.data)

    # [x]: Add a custom action named `rate` that will allow a client to send a
    #  POST and a PUT request to /meals/3/rate with a body of..
    #       {
    #           "rating": 3
    #       }
    # If the request is a PUT request, then the method should update the user's rating instead of creating a new one
    @action(methods=['POST', 'PUT'], detail=True)
    def rate(self, request, pk=None):
        """Handle POST and PUT operations to rate a meal

        Returns:
            Response -- Confirmation message and 201 CREATED or 200 OK code
        """
        try:
            current_user = User.objects.get(pk=request.auth.user_id)
            meal = Meal.objects.get(pk=pk)

            rating = request.data.get("rating")
            if rating is None:
                return Response({"reason": "Rating must be provided"}, status=status.HTTP_400_BAD_REQUEST)

            meal_rating, created = MealRating.objects.update_or_create(
                user=current_user, meal=meal, defaults={'rating': rating})

            if created:
                return Response({'message': 'Rating created'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Rating updated'}, status=status.HTTP_200_OK)

        except Meal.DoesNotExist as ex:
            return Response({"reason": ex.message}, status=status.HTTP_404_NOT_FOUND)

    # [x]: Add a custom action named `favorite` that will allow a client to send a
    #  POST request to /meals/3/favorite and add the meal as a favorite
    @action(methods=['POST'], detail=True)
    def favorite(self, request, pk):
        """Handle POST requests to add a given meal to current users list of favorite meals

        Returns:
            Response -- Confirmation message and 201 CREATED code
        """
        current_user = User.objects.get(pk=request.auth.user_id)
        meal = Meal.objects.get(pk=pk)
        meal.frequent_eaters.add(current_user)
        return Response({'message': 'User added'}, status=status.HTTP_201_CREATED)

    # [x]: Add a custom action named `unfavorite` that will allow a client to send a
    # DELETE request to /meals/3/unfavorite and remove the meal as a favorite
    @action(methods=['DELETE'], detail=True)
    def unfavorite(self, request, pk):
        """Handle DELETE requests to remove the current user from the list of meal frequent eaters

        Returns:
            Response -- 204 NO CONTENT code
        """
        current_user = User.objects.get(pk=request.auth.user_id)
        meal = Meal.objects.get(pk=pk)
        meal.frequent_eaters.remove(current_user)
        return Response(None, status=status.HTTP_204_NO_CONTENT)
