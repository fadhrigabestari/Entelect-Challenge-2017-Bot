import argparse
import json
import os
import random
# INSPIRED BY
# Python 3 sample bot by Henry Harya for initial structure
# Checkerboard search method for hunt mode (Diagonal Skew)
# Breadth First Search method for destroy mode

command_file = "command.txt"
place_ship_file = "place.txt"
game_state_file = "state.json"
output_path = '.'
map_size = 0

# Returns the index in List targets with correct coordinate
def search_cell(targets,coordinate) :
    i = 0
    n = len(targets)
    found = False
    while((i < n) and not found) :
        location = targets[i][2], targets[i][3]
        if(coordinate == location) :
            found = True
        else :
            i = i + 1
    return i

# PHASE 1 ALGORITHM
# PLACE SHIP ONTO MAP
def place_ships() :
    # Places ship in the same location everytime depending on map size
    # This is to minimize the damage of enemy's special shot
    # Randomized ship placement could result in a bad ship placement
    # Taking to acount that there wont be any player opponent

    if (map_size == 7) :
        ships = ['Battleship 7 7 west',
                'Carrier 2 7 south',
                'Cruiser 1 0 east',
                'Destroyer 7 4 north',
                'Submarine 7 1 east'
                ]
    elif (map_size == 10) :
        ships = ['Battleship 9 9 west',
                'Carrier 2 8 south',
                'Cruiser 1 0 east',
                'Destroyer 9 4 north',
                'Submarine 9 1 west'
                ]
    elif (map_size == 14) :
        ships = ['Battleship 13 13 west',
                'Carrier 2 12 south',
                'Cruiser 1 0 east',
                'Destroyer 13 4 north',
                'Submarine 13 1 west'
                ]

    with open(os.path.join(output_path, place_ship_file), 'w') as f_out:
        for ship in ships:
            f_out.write(ship)
            f_out.write('\n')
    return
# END OF PHASE 1 ALGORITHM

# PHASE 2 ALGORITHM
# HUNT ALGORITHM
# Output shot in x,y coordinate while in hunt mode
def hunt_shot(x, y, my_weapons, energy, shot_type) :
    if(shot_type[0] == "SeekerMissile" and energy >= shot_type[1]) :
        move = 7
    elif(shot_type[0] == "CrossShot" and energy >= shot_type[1]) :
        move = 6
    elif(shot_type[0] == "DoubleShot" and energy >= shot_type[1]) :
        move = random.randint(2,3)
    else :
        move = 1
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass

# Return weapon type and energy required
# In hunt mode, only return seeker missile, cross shot, and double shot according to that order
def check_hunt_weapon(my_weapons) :
    i = 0
    n = len(my_weapons)
    while(i < n) :
        if(my_weapons[i][0] == "SeekerMissile") :
            return my_weapons[i]
        else :
            i = i + 1
    while(i < n) :
        if(my_weapons[i][0] == "CrossShot") :
            return my_weapons[i]
        else :
            i = i + 1
    while(i < n) :
        if(my_weapons[i][0] == "DoubleShot") :
            return my_weapons[i]
        else :
            i = i + 1
    # No desired special shot is available
    return my_weapons[0]

# Look for a ship
# Inspired by checkerboard search method
def hunt_mode(targets, my_weapons, energy) :
    # While target cell is damaged or missed, cycle through other cell
    # Ensures to continue hunt mode where it left off after going to destroy mode
    # Search every other cell in a checkerboard pattern
    # Map size affects how checkerboard pattern search is implemented
    # Checkerboard pattern ensures that all ship can be damaged without checking all available cell
    # Cut down 50% of possible targeted cell
    # Search is done by sequential search (brute force strategy)
    i = 0
    n = len(targets)
    checkerboard = []
    shot_type = check_hunt_weapon(my_weapons)
    # Create checkerboard pattern with only available cells
    while(i < n) :
        if(not targets[i][0] and not targets[i][1]) :
            checkerboard.append(targets[i])
        if(map_size % 2 == 1) :
            i = i + 2
        else :
            if(targets[i][3] == map_size - 2) :
                i = i + 3
            elif(targets[i][3] == map_size - 1) :
                i = i + 1
            else :
                i = i + 2
    # Devide checkerboard into two different areas, left and right
    # Areas are divided according to initial targets cell, not available cells in checkerboard pattern
    i = 0
    n = len(targets)
    left_checkerboard = []
    while(i < n // 2) :
        if(not targets[i][0] and not targets[i][1]) :
            left_checkerboard.append(targets[i])
        if(map_size % 2 == 1) :
            i = i + 2
        else :
            if(targets[i][3] == map_size - 2) :
                i = i + 3
            elif(targets[i][3] == map_size - 1) :
                i = i + 1
            else :
                i = i + 2
    i = n // 2
    n = len(targets)
    right_checkerboard = []
    while(i < n) :
        if(not targets[i][0] and not targets[i][1]) :
            right_checkerboard.append(targets[i])
        if(map_size % 2 == 1) :
            i = i + 2
        else :
            if(targets[i][3] == map_size - 2) :
                i = i + 3
            elif(targets[i][3] == map_size - 1) :
                i = i + 1
            else :
                i = i + 2
    # If energy is sufficient, use special shot in a randomized location from initial checkerboard cell to the last
    if(energy >= shot_type[1]) :
        n = len(checkerboard)
        m = random.randint(0, n - 1)
        hunt_shot(checkerboard[m][2],checkerboard[m][3], my_weapons, energy, shot_type)
    else : # Energy is not sufficient
        n = len(left_checkerboard)
        m = len(right_checkerboard)
        # Hunt mode is done by randomly targeting cells in checkerboard
        # Checkerboard is divided into two parts, left and right
        # Target checkerboard part that has more available cells in it
        # Dividing checkerboard like this lessen the range in each randomized index is chosen
        # This method also ensures targeting is distributed throughout the map equally (not one sided)
        if(n >= m) : # Left checkerboard has more available cells than right checkerboard
            idx = random.randint(0,n - 1)
            hunt_shot(left_checkerboard[idx][2], left_checkerboard[idx][3], my_weapons, energy, shot_type)
        else : # Right checkerboard has more available cells than left checkerboard
            idx = random.randint(0,m - 1)
            hunt_shot(right_checkerboard[idx][2], right_checkerboard[idx][3], my_weapons, energy, shot_type)
    return
# END OF HUNT ALGORITHM

# DESTROY ALGORITHM
# Output shot in x,y coordinate while in destroy mode
def destroy_shot(x, y, my_weapons, energy, shot_type) :
    if(shot_type[0] == "DiagonalCrossShot" and energy >= shot_type[1]) :
        move = 5
    elif(shot_type[0] == "CrossShot" and energy >= shot_type[1]) :
        move = 6
    elif(shot_type[0] == "SeekerMissile" and energy >= shot_type[1]) :
        move = 7
    else :
        move = 1
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass

# Return weapon type and energy required
# In destroy mode, only return cross shot, seeker missile, and double shot according to that order
def check_destroy_weapon(my_weapons) :
    i = 0
    n = len(my_weapons)
    while(i < n) :
        if(my_weapons[i][0] == "DiagonalCrossShot") :
            return my_weapons[i]
        else :
            i = i + 1
    while(i < n) :
        if(my_weapons[i][0] == "CrossShot") :
            return my_weapons[i]
        else :
            i = i + 1
    while(i < n) :
        if(my_weapons[i][0] == "SeekerMissile") :
            return my_weapons[i]
        else :
            i = i + 1
    # No desired special shot is available
    return my_weapons[0]

# Destroy all known ships
# Inspired by BFS
def destroy_mode(state, targets, my_weapons, energy) :
    damaged_cells = [] # All cell that has been successfully
    adj_damaged_cells = [] # Adjacent cell to damaged cell that can be targeted
    shot_type = check_destroy_weapon(my_weapons)
    for cell in state['OpponentMap']['Cells']:
        if cell['Damaged'] :
            acell = cell['X'], cell['Y']
            damaged_cells.append(acell) # Insert damaged cell coordinate to damaged_cells
    # Our take on repeat until looping method in python
    repeat_until = True
    while(repeat_until) :
        damaged_cell = damaged_cells.pop(random.randint(0,len(damaged_cells) - 1)) # Pop a random cell for list of damaged_cells
        idx = search_cell(targets,damaged_cell) # Get index with search_cell function
        # Insert adjacent damaged cell to List adj_damaged_cells
        # Make sure not to access out of bounds index with 4 conditionals
        if(targets[idx][3] != 0) :
            if(not targets[idx-1][0] and not targets[idx-1][1]) :
                adj_damaged_cells.append(targets[idx-1])
        if(targets[idx][3] != map_size - 1) :
            if(not targets[idx+1][0] and not targets[idx+1][1]) :
                adj_damaged_cells.append(targets[idx+1])
        if(targets[idx][2] != map_size - 1) :
            if(not targets[idx+map_size][0] and not targets[idx+map_size][1]) :
                adj_damaged_cells.append(targets[idx+map_size])
        if(targets[idx][2] != map_size + 1) :
            if(not targets[idx-map_size][0] and not targets[idx-map_size][1]) :
                adj_damaged_cells.append(targets[idx-map_size])
        n = len(adj_damaged_cells)
        # If there is no available target adjacent to damaged cell, pop a different damaged cell from list
        # Since cell is popped from List, damaged cell wont return the same value twice in one iteration
        # If there is available target, randomly select between all available target
        if(n != 0) :
            adj_damaged_cell = random.choice(adj_damaged_cells)
            repeat_until = False
    target = adj_damaged_cell[2], adj_damaged_cell[3]
    # Use special weapon in specified location instead of normal shot for higher chance of success
    destroy_shot(target[0], target[1], my_weapons, energy, shot_type)
    # Worst case is when randomized targeting points to the correct location in the last adj_damaged_cell
    # Worst case will result in the bot knowing all adjacent cell to damaged cell
    return
# END OF DESTROY ALGORITHM

# SHIELD ALGORITHM
# Give shield command
def put_shield(x,y) :
    move = 8
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass

# Put down shield
def shield(state) :
    # Shiled will only be put down if there is a ship that is partially damaged
    # Assume that other bot also use destroy mode strategy
    # If other bot is on hunt mode (assume randomly selecting target) shield will not be put down
    # Putting down shield to defend destroy mode is better than defending againts randomized hunt mode targeting
    my_ships = []
    # Append [((Destroyed, ShipType),(Hit,X,Y)),...] to my_ships
    for ship in state['PlayerMap']['Owner']['Ships'] :
        aship = ship['Destroyed'], ship['ShipType']
        # Destroyed ship is not inserted into my_ships
        if(not aship[0]) :
            for cell in ship['Cells'] :
                acell = cell['Hit'], cell['X'], cell['Y']
                acellcell = (aship,acell)
                my_ships.append(acellcell)
    i = 0
    n = len(my_ships)
    is_hit = False
    # Find ship that is only partially damaged
    my_ship = my_ships[0][0][1]
    i = 0
    loop = True
    # Find undamaged part of the ship that is partially damaged
    while(i < n and loop) :
        if(my_ship == my_ships[i][0][1]) :
            if(not my_ships[i][1][0]) :
                my_undamaged_ship = (my_ships[i][1][1], my_ships[i][1][2])
                loop = False
            else : # Ship is partially damaged but cell is already damaged
                i = i + 1
        else : # Ship type is different
            i = i + 1
    put_shield(*my_undamaged_ship)
    return
# END OF SHIELD ALGORITHM

# Give command according to state, targets, available weapons, energy damaged ship, and destroyed ship
def command(state, targets, my_weapons, energy, damaged_ship, destroyed_ship) :
    # If damaged cell is greater than destroyed ship, enter destroyed mode
    # Greater damaged cell indicates there are still ship that has been hit but not yet destroyed
    # If sum of the length of destroyed ship is equal to damaged cell, then enter hunt mode
    # Applies greedy strategy to get as much point as possible before continuing the search for ships (destroy mode)
    charge = state['PlayerMap']['Owner']['Shield']['CurrentCharges']
    active_charge = state['PlayerMap']['Owner']['Shield']['Active']
    my_ships = []
    # None of the ships in my_ships are not destroyed
    for ship in state['PlayerMap']['Owner']['Ships'] :
        aship = ship['Destroyed']
        if(not aship) :
            my_ships.append(aship)
    n = len(my_ships)
    # If charge is available, shield is inactive, and only one ship remaining
    # Reserve as much charge as possible before using it when necessary
    if((charge > 0) and (not active_charge) and (n == 1)) :
        shield(state)
    else : # Putting down shield is unnecessary or inavailable
        if(damaged_ship > destroyed_ship) :
            destroy_mode(state, targets, my_weapons, energy) # Destroy ship
        else :
            hunt_mode(targets, my_weapons, energy) # Hunt for ship
    return
# END OF PHASE 2 ALGORITHM

# MAIN PROGRAM
def main(player_key) :
    global map_size
    # Retrieve current game state
    with open(os.path.join(output_path, game_state_file), 'r') as f_in:
        state = json.load(f_in)
    map_size = state['MapDimension']
    if state['Phase'] == 1:
        place_ships()
    else : # state['Phase'] == 2
        targets = [] # All available cell in opponent's map
        enemy_ships = [] # Remaining enemy ship
        damaged_ship = 0 # Number of cell that has been successfully damaged
        destroyed_ship = 0 # Sum of the length of all destroyed ship
        # Convert state['OpponentMap']['Ships'] from Json to List with 2 tuples
        # Count the sum of total length of all destroyed ship
        for cell in state['OpponentMap']['Ships'] :
            acell = cell['Destroyed'],cell['ShipType']
            if(acell[0]) :
                if(acell[1] == "Destroyer") :
                    destroyed_ship = destroyed_ship + 2
                elif(acell[1] == "Carrier") :
                    destroyed_ship = destroyed_ship + 5
                elif(acell[1] == "Battleship") :
                    destroyed_ship = destroyed_ship + 4
                elif(acell[1] == "Cruiser") :
                    destroyed_ship = destroyed_ship + 3
                else : # Submarine
                    destroyed_ship = destroyed_ship + 3 # Counts sum of the length of all destroyed ship
            enemy_ships.append(acell) # Insert acell to enemy_ships
        # Convert state['OpponentMap']['Cells'] from Json to List with 5 tuples
        for cell in state['OpponentMap']['Cells'] :
            acell = cell['Damaged'],cell['Missed'],cell['X'],cell['Y'],cell['ShieldHit']
            if(acell[0]) :
                 damaged_ship = damaged_ship + 1 # Counts number of cell that has been successfully damaged
            targets.append(acell) # Insert acell to targets
        energy = state['PlayerMap']['Owner']['Energy']
        my_weapons = []
        # Convert state['PlayerMap']['Owner']['Ships'] from Json to List of available weapons
        for ship in state['PlayerMap']['Owner']['Ships'] :
            aship = ship['Destroyed'],ship['ShipType'],ship['Weapons']
            if(not aship[0]) :
                for weapon in aship[2] :
                    aweapon = weapon['WeaponType'],weapon['EnergyRequired']
                    my_weapons.append(aweapon)
        command(state, targets, my_weapons, energy, damaged_ship, destroyed_ship) # Output command to game engine

if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('PlayerKey', nargs='?', help='Player key registered in the game')
    parser.add_argument('WorkingDirectory', nargs='?', default=os.getcwd(), help='Directory for the current game files')
    args = parser.parse_args()
    assert (os.path.isdir(args.WorkingDirectory))
    output_path = args.WorkingDirectory
    main(args.PlayerKey)
