import random

from django.core.management import call_command
from django.db import transaction
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from .models import Tile, Player


# Create a new game with random values (numbers between 1 and 4, and blanks)
def create_game(request):
    # Delete existing tiles and players to reset the board
    Tile.objects.all().delete()
    Player.objects.all().delete()
    call_command('flush' , interactive=False)
    print("create game called")

    # Total number of tiles (10x10 grid)
    total_tiles = 100

    # Create a new 10x10 grid of tiles
    for row in range(10):
        for col in range(10):
            rand = random.random()

            # Adjust probabilities for blanks and numbers
            if rand < 0.85:  # 15% chance of a tile being a blank ('_')
                random_value = '_'
                is_treasure = False  # No treasure for blank tiles
            else:  # 85% chance of being a number (1-4)
                random_value = str(random.randint(1, 4))
                is_treasure = True

            # Create the tile with the assigned value (either number or blank)
            tile = Tile(row=row, col=col, value=random_value, treasure=is_treasure)
            tile.save()  # Save tile to the database

    # Create players "One" and "Two" (only once)
    if Player.objects.count() == 0:
        player_one = Player(name="One", score=0)
        player_one.save()
        player_two = Player(name="Two", score=0)
        player_two.save()

    return HttpResponse('Board and players created with random values and placement.')




# Display game board
def game_display(request):
    # Get the current game state (players and tiles)
    tiles = Tile.objects.all()  # Fetch all tiles from the database
    players = Player.objects.all()

    board_string = ""

    # Organize tiles by row and column in a 10x10 grid
    for row in range(10):
        for col in range(10):
            # Retrieve the tile based on row and column using efficient query
            tile = tiles.filter(row=row, col=col).first()
            # print(tile.value)

            if tile:
                # Display the tile's value based on its state
                if tile.value == '_':
                    board_string += "_ "  # Blank tile
                else:
                    board_string += f"{tile.value} "  # Mark other picked tiles

        # Add a newline after each row
        board_string += "<br>"


    return render(request, 'game/board.html', {'board': board_string, 'players': players})

# Handle player picking a tile
@transaction.atomic
def pick_tile(request, player_name, row, column):
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


