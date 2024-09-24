from django.shortcuts import render
from django.http import JsonResponse
import random

# Global variables to track the grid and the last placed number
grid = None
last_number = 1
last_position = None
placed_numbers = []  # Track all placed numbers for rollback

# Valid positions for number placement (the inner 5x5 grid only)
valid_positions = [(i, j) for i in range(1, 6) for j in range(1, 6)]


def game_view(request):
    global grid, last_number, last_position, placed_numbers
    grid_size = 7

    if grid is None:  # Initialize the grid on the first visit
        grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        # Randomly place number 1 in the 5x5 inner grid (indices 1-5 for both row and column)
        random_row = random.randint(1, 5)
        random_col = random.randint(1, 5)
        grid[random_row][random_col] = last_number
        last_position = (random_row, random_col)  # Store the position of the last placed number
        placed_numbers.append((random_row, random_col, last_number))  # Track placed number

    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'place':
            row = int(request.POST.get('row'))
            col = int(request.POST.get('col'))

            # Check if the placement is valid
            if (grid[row][col] is None and
                    (abs(row - last_position[0]) <= 1 and abs(col - last_position[1]) <= 1) and
                    (row, col) not in [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),
                                       (1, 0), (1, 6), (2, 0), (2, 6), (3, 0), (3, 6), (4, 0), (4, 6),
                                       (5, 0), (5, 6), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
                                       (6, 6)]):  # Not in blue or yellow cells

                # Update the grid
                last_number += 1  # Increment the number for the next placement
                grid[row][col] = last_number  # Place the next number
                last_position = (row, col)  # Store the last position
                placed_numbers.append((row, col, last_number))  # Track the placement

                # Check for level completion after placing the number
                if last_number >= 25:
                    return JsonResponse({
                        'status': 'success',
                        'grid': grid,
                        'finished': True,
                        'message': 'Congratulations! You have completed Level 1. Do you want to proceed to Level 2?'
                    })

                return JsonResponse({
                    'status': 'success',
                    'grid': grid
                })
            else:
                return JsonResponse({'status': 'deadend'})

        elif action == 'rollback':
            if placed_numbers and last_number > 2:  # Rollback only if there's a number to remove and it's not the first number
                # Remove the last placed number
                last_row, last_col, last_num = placed_numbers.pop()  # Get last placed number's details

                if last_num > 1:  # Only clear if it's greater than 1
                    grid[last_row][last_col] = None  # Clear the last placed number

                last_number = last_num  # Set last number to the one just rolled back

                # Update the last position to the new last number
                if placed_numbers:
                    last_row, last_col, last_num = placed_numbers[-1]  # Get the new last position
                    last_position = (last_row, last_col)  # Update last position
                else:
                    last_position = None  # No last position if all numbers are rolled back

                # Update the grid with the rolled-back number as clickable
                return JsonResponse({
                    'status': 'rollback',
                    'grid': grid,
                    'last_number': last_number
                })

        return JsonResponse({'status': 'invalid'})

    context = {
        'grid': grid,
    }

    return render(request, 'game/game.html', context)
