# Generated by Django 3.1.3 on 2023-05-11 15:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteMeal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='FavoriteRestaurant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55)),
                ('frequent_eaters', models.ManyToManyField(related_name='favorited_meals', through='favamealapi.FavoriteMeal', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=55, unique=True)),
                ('address', models.CharField(max_length=255)),
                ('favoriters', models.ManyToManyField(related_name='favorited_restaurants', through='favamealapi.FavoriteRestaurant', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MealRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
                ('meal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mealrating', to='favamealapi.meal')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mealrating', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='meal',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='favamealapi.restaurant'),
        ),
        migrations.AddField(
            model_name='favoriterestaurant',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userfavoriterestaurants', to='favamealapi.restaurant'),
        ),
        migrations.AddField(
            model_name='favoriterestaurant',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userfavoriterestaurants', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='favoritemeal',
            name='meal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userfavoritemeals', to='favamealapi.meal'),
        ),
        migrations.AddField(
            model_name='favoritemeal',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userfavoritemeals', to=settings.AUTH_USER_MODEL),
        ),
    ]
