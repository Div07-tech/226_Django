# models.py
from django.db import models

# models.py
class Tile(models.Model):
    row = models.IntegerField()  # Row position
    col = models.IntegerField()  # Column position
    value = models.CharField(max_length=1, default='_')  # Value can be '1', '2', '3', '4' or '_'
    treasure = models.BooleanField(default=False)  # Indicates whether the tile has treasure

    def __str__(self):
        return f"Tile ({self.row}, {self.col}) - Value: {self.value}, Treasure: {self.treasure}"


class Player(models.Model):
    name = models.CharField(max_length=100)  # Name of the player
    score = models.IntegerField(default=0)  # Player's score, default is 0

    def __str__(self):
        return f"Player: {self.name} (Score: {self.score})"
