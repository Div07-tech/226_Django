from django.contrib import admin

# Register your models here.
from .models import Player, Tile
admin.site.register(Player)
admin.site.register(Tile)
