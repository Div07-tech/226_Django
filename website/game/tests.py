
from django.test import TestCase
from django.urls import reverse
from .models import Tile, Player


#testing player
class test_player(TestCase):
   def testing_players(self):
       self.client.post('/game/create')
       player_count = Player.objects.all()
       # Ensure there are exactly 2 players
       self.assertEqual(len(player_count), 2)
       # Ensure players have the correct attributes
       self.assertEqual(player_count[0].name, "One")
       self.assertEqual(player_count[1].name, "Two")
       print("Two players are created")

#checking the number of tiles
class tiles_Testing(TestCase):
    def test_tiles_created(self):
        self.client.post('/game/create')
        tile_count = Tile.objects.count()
        self.assertEqual(tile_count, 100)
        print(f"100 tiles are created")

#testing the treasures
class creating_treasures(TestCase):
    def test_create_treasures(self):
        self.client.post('/game/create')
        treasure_tiles = Tile.objects.filter(treasure=True)
        print("Treasure tiles values:")
        self.assertTrue(len(treasure_tiles) > 0)

#testing the picking a treasure causes the Player's score to be updated correctly
class Pick_Treasure_Test(TestCase):
    def test_pick_treasure_updates_score(self):
        self.client.post('/game/create')
        self.player_one = Player.objects.get(name="One")
        # self.player_two = Player.objects.get(name="Two")
        self.treasure_tile = Tile.objects.filter(treasure=True).first()
        # Ensure the player's initial score is 0
        initial_score = self.player_one.score

        # Get the value of the treasure on the tile before picking it
        treasure_value = int(self.treasure_tile.value)

        # the action of player one picking the treasure tile at (row, col)
        url = reverse('pick_tile', args=[self.player_one.name, self.treasure_tile.row, self.treasure_tile.col])
        self.client.post(url)

        # Step 4: Fetch the updated player score and tile
        self.player_one = Player.objects.get(id=self.player_one.id)
        self.treasure_tile = Tile.objects.get(id=self.treasure_tile.id)

        # Step 5: Verify that the player's score is updated correctly
        self.assertEqual(self.player_one.score, initial_score + treasure_value,"Player's score was not updated correctly.")

        # Step 6: Ensure the tile's value is now '_', indicating it has been picked
        self.assertEqual(self.treasure_tile.value, '_', "The treasure tile value was not updated to '_'.")
        self.assertFalse(self.treasure_tile.treasure, "The tile's treasure flag was not updated.")
        print(f"Player's updated score: {self.player_one.score}")
