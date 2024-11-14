from django.urls import path
from . import views
urlpatterns = [
path('pick/<str:player_name>/<int:row>/<int:column>/', views.pick_tile, name='pick_tile'),
path('create', views.create_game, name='create_game'),
path('', views.game_display, name='game_display'),
]