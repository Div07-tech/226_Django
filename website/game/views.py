import random

from django.core.management import call_command
from django.db import transaction
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from .models import Tile, Player

class Board:
    def __init__(self,n,t):
        if n < 2 :
            raise ValueError("Invalid row or column")
        if t < 0:
            raise ValueError("Number cannot be negative")
        self.n = n
        self.t = t
        self.board = [['_' for _ in range(n)] for _ in range(n)]
        self.place_treasures()

        # this method search for random positions in every direction
    def can_place_treasure(self, row, col, label, direction):
        if direction == 'h':
            if col + label > self.n:
                return False
            for i in range(label):
                if self.board[row][col + i] != '_':
                    return False
        else:
            if row + label > self.n:
                return False
            for i in range(label):
                if self.board[row + i][col] != '_':
                    return False
        return True

    def place_treasures(self):

        for label in range(1, self.t + 1):
            placed = False
            while not placed:
                row, col = random.randint(0, self.n - 1), random.randint(0, self.n - 1)
                if self.board[row][col] == '_':
                    direction = random.choice(['h', 'v'])
                    if self.can_place_treasure(row, col, label, direction):
                        self.place_treasure(row, col, label, direction)
                        placed = True
    def place_treasure(self, row, col, label, direction):
        for i in range(label):
            if direction == 'h':
                self.board[row][col + i] = str(label)
            else:
                self.board[row + i][col] = str(label)
    #method for locating number at specific location.
    def pick(self, row, col):
        try:
            treasure = int(self.board[row][col])
            self.board[row][col] = '_'
            return treasure
        except:
            return 0

    def __str__(self):
        result = ""
        for row in self.board:
            result += " ".join(row) + "\n"
        return result.strip()
# Create a new game with random values (numbers between 1 and 4, and blanks)
def create_game(request):
    # Delete existing tiles and players to reset the board
    Tile.objects.all().delete()
    Player.objects.all().delete()
    call_command('flush', interactive=False)
    print("create game called")

    # Initialize a 10x10 board with 4 treasure types (1, 2, 3, 4)
    board = Board(n=10, t=4)

    # Now save the board to the database
    for row in range(board.n):
        for col in range(board.n):
            value = board.board[row][col]  # Value of the tile (either '_', '1', '2', etc.)
            is_treasure = value != '_'
            # Create the tile and save to database
            tile = Tile(row=row, col=col, value=value, treasure=is_treasure)
            tile.save()

    # Create players "One" and "Two" (only once)
    if Player.objects.count() == 0:
        player_one = Player(name="One", score=0)
        player_one.save()
        player_two = Player(name="Two", score=0)
        player_two.save()

    return HttpResponse('Board and players created with random values and placement.')

def game_display(request):
    # Get the current game state (players and tiles)
    tiles = Tile.objects.all()  # Fetch all tiles from the database
    players = Player.objects.all()

    # Create a 2D grid (list of lists) to represent the board
    board = [[None for _ in range(10)] for _ in range(10)]

    # Organize tiles by row and column in a 10x10 grid
    for tile in tiles:
        # Place each tile's value into the appropriate position in the grid
        board[tile.row][tile.col] = tile

    # Pass the board grid and players to the template
    return render(request, 'game/board.html', {'board': board, 'players': players})


# Handle player picking a tile
@transaction.atomic
def pick_tile(request, player_name, row,
              column):
    try:
        # Validate that the row and column are within bounds (0-9)
        if row < 0 or row >= 10 or column < 0 or column >= 10:
            raise ValueError("Invalid row or column.")

        # Fetch the player and lock it for update (to prevent race conditions)
        player = Player.objects.get(name=player_name)
        print(player)

        # Fetch the tile and lock it for update to prevent concurrent access
        tile = Tile.objects.select_for_update().get(row=row, col=column)
        print(tile)
        # Perform the tile and player update
        if tile.value:
            print(tile.value)
            player.score += int(tile.value) # Convert the value (1-4) to an integer and update the score
            tile.value = '_'
            tile.treasure = False
        # Save the tile and player after changes
        tile.save()
        player.save()
        print(player.score)

        # Redirect to display updated game state
        return redirect('game_display')

    except Tile.DoesNotExist:
        raise Http404("Tile does not exist.")
    except Player.DoesNotExist:
        raise Http404("Player does not exist.")


