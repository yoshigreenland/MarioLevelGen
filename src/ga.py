import copy
import heapq
import metrics
import multiprocessing.pool as mpool
import os
import random
import shutil
import time
import math

width = 200
height = 16

options = [
    "-",  # an empty space
    "X",  # a solid wall
    "?",  # a question mark block with a coin
    "M",  # a question mark block with a mushroom
    "B",  # a breakable block
    "o",  # a coin
    "|",  # a pipe segment
    "T",  # a pipe top
    "E",  # an enemy
    #"f",  # a flag, do not generate
    #"v",  # a flagpole, do not generate
    #"m"  # mario's start position, do not generate
]

# The level as a grid of tiles


class Individual_Grid(object):
    __slots__ = ["genome", "_fitness"]

    def __init__(self, genome):
        self.genome = copy.deepcopy(genome)
        self._fitness = None

    # Update this individual's estimate of its fitness.
    # This can be expensive so we do it once and then cache the result.
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Print out the possible measurements or look at the implementation of metrics.py for other keys:
        # print(measurements.keys())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Modify this, and possibly add more metrics.  You can replace this with whatever code you like.
        coefficients = dict(
            meaningfulJumpVariance=0.8,
            negativeSpace=0.6,
            pathPercentage=0.5,
            emptyPercentage=0.8,
            linearity=-0.5,
            solvability=2.0
        )
        self._fitness = sum(map(lambda m: coefficients[m] * measurements[m],
                                coefficients))
        return self

    # Return the cached fitness value or calculate it as needed.
    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    def findNeighbors(self,genome, point:tuple, within:int):
        # print(f"[#] Running findNeighors({genome}, {point}, {within})")
        x,y = point
        neighbors = []
        currSize = 2
        startOffset = 0
        dir = 1
        for currDist in range(1,within+1):
            neighbors.append([])
            # print(f"[?] Current distance is {currDist}")
            # print(f"[?] Neighbors is {neighbors}")
            # print(f"[?] startOffset is {startOffset}")
            # print(f"[?] currSize is {currSize}")

            # print(f"[#] Checking top side...")
            for currSquare in range(0,currSize-startOffset):
                newX = x - startOffset + currSquare
                newY = y - currDist
                if (newX < 0 or newX >= len(genome[0])):
                    # print(f"\t[#] currSquare{currSquare} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                if (newY < 0 or newY >= len(genome)):
                    # print(f"\t[#] currDist {currDist} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                neighbor = genome[newY][newX]
                # print(f"\t[?] newX = {newX}")
                # print(f"\t[?] newY = {currDist}")
                # print(f"\t[?] Current neighbor is {neighbor}")
                neighbors[currDist-1].append(neighbor)
                # print()

            # print(f"[#] Checking right side...")
            for currSquare in range(0,currSize-startOffset):
                newX = x + currDist
                newY = y - startOffset + currSquare
                if (newX < 0 or newX >= len(genome[0])):
                    # print(f"\t[#] currSquare{currSquare} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                if (newY < 0 or newY >= len(genome)):
                    # print(f"\t[#] currDist {currDist} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                neighbor = genome[newY][newX]
                # print(f"\t[?] newX = {newX}")
                # print(f"\t[?] newY = {currDist}")
                # print(f"\t[?] Current neighbor is {neighbor}")
                neighbors[currDist-1].append(neighbor)
                # print()

            # backwards
            # print(f"[#] Checking bottom side...")
            for currSquare in range(0,currSize-startOffset):
                newX = x + startOffset - currSquare
                newY = y + currDist
                if (newX < 0 or newX >= len(genome[0])):
                    # print(f"\t[#] currSquare{currSquare} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                if (newY < 0 or newY >= len(genome)):
                    # print(f"\t[#] currDist {currDist} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                neighbor = genome[newY][newX]
                # print(f"\t[?] newX = {newX}")
                # print(f"\t[?] newY = {currDist}")
                # print(f"\t[?] Current neighbor is {neighbor}")
                neighbors[currDist-1].append(neighbor)
                # print()

            # print(f"[#] Checking left side...")
            for currSquare in range(0,currSize-startOffset):
                newX = x - currDist
                newY = y + startOffset - currSquare
                if (newX < 0 or newX >= len(genome[0])):
                    # print(f"\t[#] currSquare{currSquare} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                if (newY < 0 or newY >= len(genome)):
                    # print(f"\t[#] currDist {currDist} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                neighbor = genome[newY][newX]
                # print(f"\t[?] newX = {newX}")
                # print(f"\t[?] newY = {currDist}")
                # print(f"\t[?] Current neighbor is {neighbor}")
                neighbors[currDist-1].append(neighbor)
                # print()
            currSize += 3
            startOffset += 1

        return(neighbors)

    def distFromX(self, genome, point:tuple, within:int, targets:list):
        # print(f"[#] Running distFromX({genome}, {point}, {within}, {targets})")
        x,y = point
        neighbors = []
        currSize = 2
        startOffset = 0
        dir = 1
        for currDist in range(1,within+1):
            neighbors.append([])
            # print(f"[?] Current distance is {currDist}")
            # print(f"[?] Neighbors is {neighbors}")
            # print(f"[?] startOffset is {startOffset}")
            # print(f"[?] currSize is {currSize}")

            # print(f"[#] Checking top side...")
            for currSquare in range(0,currSize-startOffset):
                newX = x - startOffset + currSquare
                newY = y - currDist
                if (newX < 0 or newX >= len(genome[0])):
                    # print(f"\t[#] currSquare{currSquare} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                if (newY < 0 or newY >= len(genome)):
                    # print(f"\t[#] currDist {currDist} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                neighbor = genome[newY][newX]
                # print(f"\t[?] newX = {newX}")
                # print(f"\t[?] newY = {currDist}")
                # print(f"\t[?] Current neighbor is {neighbor}")
                if (neighbor in targets):
                    return(currDist)
                else:
                    neighbors[currDist-1].append(neighbor)
            #     print()

            # print(f"[#] Checking right side...")
            for currSquare in range(0,currSize-startOffset):
                newX = x + currDist
                newY = y - startOffset + currSquare
                if (newX < 0 or newX >= len(genome[0])):
                    # print(f"\t[#] currSquare{currSquare} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                if (newY < 0 or newY >= len(genome)):
                    # print(f"\t[#] currDist {currDist} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                neighbor = genome[newY][newX]
                # print(f"\t[?] newX = {newX}")
                # print(f"\t[?] newY = {currDist}")
                # print(f"\t[?] Current neighbor is {neighbor}")
                if (neighbor in targets):
                    return(currDist)
                else:
                    neighbors[currDist-1].append(neighbor)
            #     print()

            # # backwards
            # print(f"[#] Checking bottom side...")
            for currSquare in range(0,currSize-startOffset):
                newX = x + startOffset - currSquare
                newY = y + currDist
                if (newX < 0 or newX >= len(genome[0])):
                    # print(f"\t[#] currSquare{currSquare} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                if (newY < 0 or newY >= len(genome)):
                    # print(f"\t[#] currDist {currDist} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                neighbor = genome[newY][newX]
                # print(f"\t[?] newX = {newX}")
                # print(f"\t[?] newY = {currDist}")
                # print(f"\t[?] Current neighbor is {neighbor}")
                if (neighbor in targets):
                    return(currDist)
                else:
                    neighbors[currDist-1].append(neighbor)
                # print()

            # print(f"[#] Checking left side...")
            for currSquare in range(0,currSize-startOffset):
                newX = x - currDist
                newY = y + startOffset - currSquare
                if (newX < 0 or newX >= len(genome[0])):
                    # print(f"\t[#] currSquare{currSquare} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                if (newY < 0 or newY >= len(genome)):
                    # print(f"\t[#] currDist {currDist} out of range")
                    neighbors[currDist-1].append(None)
                    continue
                neighbor = genome[newY][newX]
                # print(f"\t[?] newX = {newX}")
                # print(f"\t[?] newY = {currDist}")
                # print(f"\t[?] Current neighbor is {neighbor}")
                if (neighbor in targets):
                    return(currDist)
                else:
                    neighbors[currDist-1].append(neighbor)
                # print()
            currSize += 3
            startOffset += 1

        return(-1)

    def heightFromGround(self,genome, x,y):
        height = 0
        i = 1
        while (y+i < len(genome) and genome[y+i][x] not in ('X', 'M', '?', 'B', 'T','|')):
            height += 1
            i += 1

        return(height)

    # Mutate a genome into a new genome.  Note that this is a _genome_, not an individual!
    def mutate(self, genome):
        # STUDENT implement a mutation operator, also consider not mutating this individual
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
        '''
            To do:
                Make mutation not completely random (I.e. an informed random).
                    For example, increase the chance for a floating block if 
                    its neighbor is a block or if it is within three spaces 
                    above another block; increase chance for mshroom box if 
                    left & right neighbors are smashable or if it's one above
                    the ground; or increase the chance for coin if within one 
                    space of another coin or if within 3 spaces of ground with
                    air between
        '''
        mutChance_perNome = 60
        # ^ Chance for mutation at all
        # v Chance for mutation on this specific cell
        mutChance_perCell = 10

        # mutOptions = { # Each instance represents a 5% chance
        #     '-': 30,
        #     'X': 30,
        #     '?': 30,
        #     'M': 30,
        #     'B': 30,
        #     'o': 30,
        #     '|': 30,
        #     'T': 30,
        #     'E': 30
        # }


        if (random.randrange(1,100) > mutChance_perNome):
            # print("\t\t\t[#] Did not mutate")
            return(False) #return without mutating
        else:
            left = 0
            right = width
            # print(f"\t\t\t[?] Data:\n\t\t\t\tleft: {left}\n\t\t\t\tright: {right}\n\t\t\t\theight: {height}")
            for y in range(height-1,0,-1):
                for x in range(left, right):
                    mutOptions = options.copy()
                    mutOptions.extend(['-','-','-','-','-','-','-','-','-','-'])
                    myNeighbors = self.findNeighbors(genome,(x,y),1)
                    if ('m' in myNeighbors and y != len(genome)-1):
                        genome[y][x] = '-'
                    elif (genome[y][x] != 'm' and genome[y][x] != 'v' and genome[y][x] != 'f'):
                        currVal = genome[y][x]

                        # If I'm floating midair and I'm a ground, the block below me must also be a ground
                        if (currVal == 'X' and self.heightFromGround(genome,x,y) != 0):
                            genome[y+1][x] = 'X'
                            continue
                        
                        # If I'm a pipe-top and I'm underneath another pipe piece, I must be a pipe-body
                        if (currVal == 'T' and myNeighbors[0][0] in ('|', 'T')):
                            genome[y][x] = '|'
                            continue

                        # If I'm a pipe-body and there is not another pipe piece above me, I must be a pipe-top
                        if (currVal == '|' and myNeighbors[0][0] not in ('|', 'T')):
                            genome[y][x] = 'T'
                            continue

                        # If I'm floating midair and I'm a pipe piece, the block below me must be a pipe-body
                        if (currVal in ('|','T') and self.heightFromGround(genome,x,y) != 0):
                            genome[y+1][x] = '|'
                            continue

                        # If I don't have to be anything in particular, I can mutate
                        if (random.randrange(0,100) <= mutChance_perCell):
                            myNeighbors = self.findNeighbors(genome,(x,y),1)

                            # If I'm a ? block and there is air, an enemy, or a coin above me, I can be a mushroom block
                            if (genome[y][x] == '?'):
                                if (myNeighbors[0][0] == 'E' or myNeighbors[0][0] == '-' or myNeighbors[0][0] == 'o'):
                                    mutOptions.extend(['M','?','?','?'])

                            # If I'm within 3 spaces of another platform, I can be a platform
                            if (self.distFromX(genome,(x,y),3,['B','?','M','T','X'])):
                                mutOptions.extend(['B','B','X','X','T','T','?'])

                            # If there is a platform next to me, I can be a platform
                            if (myNeighbors[0][6] in ('B','?','M','|','T','X')):
                                mutOptions.extend(['B','?','M','|','T','X',myNeighbors[0][6],myNeighbors[0][6]])
                            elif (myNeighbors[0][2] in ('B','?','M','|','T','X')):
                                mutOptions.extend(['B','?','M','|','T','X',myNeighbors[0][2],myNeighbors[0][2]])

                            # If I'm surrounded by bricks and have air underneath me, I can be a ? block
                            if (myNeighbors[0][6] == 'B' and myNeighbors[0][2] == 'B' and myNeighbors[0][4] == '-'):
                                mutOptions.extend(['?','?','?','?'])

                            # If I'm above or below a ground, I can be ground
                            if (myNeighbors[0][4] == 'X' or myNeighbors[0][0] == 'X'):
                                mutOptions.extend(['X','X','X','X'])

                            # If I'm on a pipe or ground, I can be a pipe
                            if (myNeighbors[0][4] in ('|', 'T', 'X')):
                                mutOptions.extend(['|','|','|'])

                            # If I'm floating in midair, I cannot be a pipe or ground
                            if (self.heightFromGround(genome,x,y) != 0):
                                for banned in ('X','T','|'):
                                    while (banned in mutOptions):
                                        mutOptions.remove(banned)

                            # If I'm on a platform and I'm atleast 5 spaces away from another enemy or the player, I can be an enemy
                            if (self.distFromX(genome,(x,y),5,['E','m']) < 0 and self.heightFromGround(genome,x,y) == 0):
                                mutOptions.extend(['E'])

                            # If I'm floating at least 2 spaces off the ground and I'm within 3 spaces of a platform or another coin, I can be a coin
                            if (self.heightFromGround(genome,x,y) >= 2 and self.distFromX(genome,(x,y),3,['B','?','M','X','T','E','|'])):
                                mutOptions.extend(['o','o'])

                            #If I'm at the bottom level, I can only be a ground, air, or a pipe-top
                            if (y >= len(genome)-1):
                                for banned in ('o','B','?','M','|','E'):
                                    while (banned in mutOptions):
                                        mutOptions.remove(banned)
                                mutOptions.extend(['X','T','-'])

                            newVal = random.choice(mutOptions)
                            # print(f"\t\t\t [?] Mutation options for this cell: {mutOptions}")
                            # print(f"\t\t\t [#] Mutated! Cell ({x},{y}): {currVal} -> {newVal}")
                            genome[y][x] = newVal
                            
            self.genome = genome
            return(True)

    # Create zero or more children from self and other
    def generate_children(self, other):
        # print(f"\t[?] Calling generate_children with {self} and {other}")
        new_genome = copy.deepcopy(self.genome)
        # Leaving first and last columns alone...
        # do crossover with other
        left = width//2
        right = width - left
        # print(f"\t\t[?] Data:\n\t\t\tleft: {left}\n\t\t\tright: {right}\n\t\t\tlen(self.genome) AKA len(new_genome): {len(self.genome)}\n\t\t\tlen(other.genome): {len(other.genome)}\n\t\t\tnew_genome(len: {len(new_genome)}): {new_genome}")
        for y in range(height):
            for x in range(left, right):
                # STUDENT Which one should you take?  Self, or other?  Why?
                # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
                new_genome[y][x] = other.genome[y][x]
        newChild = Individual_Grid(new_genome)
        newChild.mutate(new_genome)
        # do mutation; note we're returning a one-element tuple here
        return(newChild)

    # Turn the genome into a level string (easy for this genome)
    def to_level(self):
        return self.genome

    # These both start with every floor tile filled with Xs
    # STUDENT Feel free to change these
    @classmethod
    def empty_individual(cls):
        g = [["-" for col in range(width)] for row in range(height)]
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        for col in range(8, 14):
            g[col][-1] = "f"
        for col in range(14, 16):
            g[col][-1] = "X"
        return cls(g)

    @classmethod
    def random_individual(cls):
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        g = [random.choices(options, k=width) for row in range(height)]
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        g[8:14][-1] = ["f"] * 6
        g[14:16][-1] = ["X", "X"]
        return cls(g)


def offset_by_upto(val, variance, min=None, max=None):
    val += random.normalvariate(0, variance**0.5)
    if min is not None and val < min:
        val = min
    if max is not None and val > max:
        val = max
    return int(val)


def clip(lo, val, hi):
    if val < lo:
        return lo
    if val > hi:
        return hi
    return val

# Inspired by https://www.researchgate.net/profile/Philippe_Pasquier/publication/220867545_Towards_a_Generic_Framework_for_Automated_Video_Game_Level_Creation/links/0912f510ac2bed57d1000000.pdf


class Individual_DE(object):
    # Calculating the level isn't cheap either so we cache it too.
    __slots__ = ["genome", "_fitness", "_level"]

    # Genome is a heapq of design elements sorted by X, then type, then other parameters
    def __init__(self, genome):
        self.genome = list(genome)
        heapq.heapify(self.genome)
        self._fitness = None
        self._level = None

    # Calculate and cache fitness
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Add more metrics?
        # STUDENT Improve this with any code you like
        coefficients = dict(
            meaningfulJumpVariance=0.5,
            negativeSpace=0.6,
            pathPercentage=0.5,
            emptyPercentage=0.6,
            linearity=-0.5,
            solvability=2.0
        )
        penalties = 0
        # STUDENT For example, too many stairs are unaesthetic.  Let's penalize that
        if len(list(filter(lambda de: de[1] == "6_stairs", self.genome))) > 5:
            penalties -= 2
        # STUDENT If you go for the FI-2POP extra credit, you can put constraint calculation in here too and cache it in a new entry in __slots__.
        self._fitness = sum(map(lambda m: coefficients[m] * measurements[m],
                                coefficients)) + penalties
        return self

    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    def mutate(self, new_genome):
        # STUDENT How does this work?  Explain it in your writeup.
        # STUDENT consider putting more constraints on this, to prevent generating weird things
        if random.random() < 0.1 and len(new_genome) > 0:
            to_change = random.randint(0, len(new_genome) - 1)
            de = new_genome[to_change]
            new_de = de
            x = de[0]
            de_type = de[1]
            choice = random.random()
            if de_type == "4_block":
                y = de[2]
                breakable = de[3]
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                else:
                    breakable = not de[3]
                new_de = (x, de_type, y, breakable)
            elif de_type == "5_qblock":
                y = de[2]
                has_powerup = de[3]  # boolean
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                else:
                    has_powerup = not de[3]
                new_de = (x, de_type, y, has_powerup)
            elif de_type == "3_coin":
                y = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                new_de = (x, de_type, y)
            elif de_type == "7_pipe":
                h = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    h = offset_by_upto(h, 2, min=2, max=height - 4)
                new_de = (x, de_type, h)
            elif de_type == "0_hole":
                w = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    w = offset_by_upto(w, 4, min=1, max=width - 2)
                new_de = (x, de_type, w)
            elif de_type == "6_stairs":
                h = de[2]
                dx = de[3]  # -1 or 1
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    h = offset_by_upto(h, 8, min=1, max=height - 4)
                else:
                    dx = -dx
                new_de = (x, de_type, h, dx)
            elif de_type == "1_platform":
                w = de[2]
                y = de[3]
                madeof = de[4]  # from "?", "X", "B"
                if choice < 0.25:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.5:
                    w = offset_by_upto(w, 8, min=1, max=width - 2)
                elif choice < 0.75:
                    y = offset_by_upto(y, height, min=0, max=height - 1)
                else:
                    madeof = random.choice(["?", "X", "B"])
                new_de = (x, de_type, w, y, madeof)
            elif de_type == "2_enemy":
                pass
            new_genome.pop(to_change)
            heapq.heappush(new_genome, new_de)
        return new_genome

    def generate_children(self, other):
        # STUDENT How does this work?  Explain it in your writeup.
        pa = random.randint(0, len(self.genome) - 1)
        pb = random.randint(0, len(other.genome) - 1)
        a_part = self.genome[:pa] if len(self.genome) > 0 else []
        b_part = other.genome[pb:] if len(other.genome) > 0 else []
        ga = a_part + b_part
        b_part = other.genome[:pb] if len(other.genome) > 0 else []
        a_part = self.genome[pa:] if len(self.genome) > 0 else []
        gb = b_part + a_part
        # do mutation
        return Individual_DE(self.mutate(ga)), Individual_DE(self.mutate(gb))

    # Apply the DEs to a base level.
    def to_level(self):
        if self._level is None:
            base = Individual_Grid.empty_individual().to_level()
            for de in sorted(self.genome, key=lambda de: (de[1], de[0], de)):
                # de: x, type, ...
                x = de[0]
                de_type = de[1]
                if de_type == "4_block":
                    y = de[2]
                    breakable = de[3]
                    base[y][x] = "B" if breakable else "X"
                elif de_type == "5_qblock":
                    y = de[2]
                    has_powerup = de[3]  # boolean
                    base[y][x] = "M" if has_powerup else "?"
                elif de_type == "3_coin":
                    y = de[2]
                    base[y][x] = "o"
                elif de_type == "7_pipe":
                    h = de[2]
                    base[height - h - 1][x] = "T"
                    for y in range(height - h, height):
                        base[y][x] = "|"
                elif de_type == "0_hole":
                    w = de[2]
                    for x2 in range(w):
                        base[height - 1][clip(1, x + x2, width - 2)] = "-"
                elif de_type == "6_stairs":
                    h = de[2]
                    dx = de[3]  # -1 or 1
                    for x2 in range(1, h + 1):
                        for y in range(x2 if dx == 1 else h - x2):
                            base[clip(0, height - y - 1, height - 1)][clip(1, x + x2, width - 2)] = "X"
                elif de_type == "1_platform":
                    w = de[2]
                    h = de[3]
                    madeof = de[4]  # from "?", "X", "B"
                    for x2 in range(w):
                        base[clip(0, height - h - 1, height - 1)][clip(1, x + x2, width - 2)] = madeof
                elif de_type == "2_enemy":
                    base[height - 2][x] = "E"
            self._level = base
        return self._level

    @classmethod
    def empty_individual(_cls):
        # STUDENT Maybe enhance this
        g = []
        return Individual_DE(g)

    @classmethod
    def random_individual(_cls):
        # STUDENT Maybe enhance this
        elt_count = random.randint(8, 128)
        g = [random.choice([
            (random.randint(1, width - 2), "0_hole", random.randint(1, 8)),
            (random.randint(1, width - 2), "1_platform", random.randint(1, 8), random.randint(0, height - 1), random.choice(["?", "X", "B"])),
            (random.randint(1, width - 2), "2_enemy"),
            (random.randint(1, width - 2), "3_coin", random.randint(0, height - 1)),
            (random.randint(1, width - 2), "4_block", random.randint(0, height - 1), random.choice([True, False])),
            (random.randint(1, width - 2), "5_qblock", random.randint(0, height - 1), random.choice([True, False])),
            (random.randint(1, width - 2), "6_stairs", random.randint(1, height - 4), random.choice([-1, 1])),
            (random.randint(1, width - 2), "7_pipe", random.randint(2, height - 4))
        ]) for i in range(elt_count)]
        return Individual_DE(g)


Individual = Individual_Grid


def generate_successors(population):
    # print(f"\t[?] Population size: {len(population)}")
    results = []
    pop_limit = len(population);
    ideal_proportion = 0.25
    fit_sorted = sorted(population, key=Individual.fitness, reverse=True)
    for i in range(pop_limit):
        dad = fit_sorted[random.randint(0, int(pop_limit * ideal_proportion))]
        mom = fit_sorted[random.randint(0, int(pop_limit * ideal_proportion))]
        results.append(dad.generate_children(mom))
    return results


def ga():
    # STUDENT Feel free to play with this parameter
    pop_limit = 480
    # Code to parallelize some computations
    batches = os.cpu_count()
    if pop_limit % batches != 0:
        print("It's ideal if pop_limit divides evenly into " + str(batches) + " batches.")
    batch_size = int(math.ceil(pop_limit / batches))
    with mpool.Pool(processes=os.cpu_count()) as pool:
        init_time = time.time()
        # STUDENT (Optional) change population initialization
        population = [Individual.random_individual() if random.random() < 0.9
                      else Individual.empty_individual()
                      for _g in range(pop_limit)]
        # print(f"[?] Initial Population: {population}")
        # But leave this line alone; we have to reassign to population because we get a new population that has more cached stuff in it.
        population = pool.map(Individual.calculate_fitness,
                              population,
                              batch_size)
        # print(f"[?] Population after pool: {population}")
        init_done = time.time()
        print("Created and calculated initial population statistics in:", init_done - init_time, "seconds")
        generation = 0
        start = time.time()
        now = start
        print("Use ctrl-c to terminate this loop manually.")
        try:
            while True:
                now = time.time()
                # Print out statistics
                if generation > 0:
                    best = max(population, key=Individual.fitness)
                    print("\tGeneration:", str(generation))
                    print("\t\tMax fitness:", str(best.fitness()))
                    print("\t\tAverage generation time:", (now - start) / generation)
                    print("\t\tNet time:", now - start)
                    with open("levels/last.txt", 'w') as f:
                        for row in best.to_level():
                            f.write("".join(row) + "\n")
                generation += 1
                # STUDENT Determine stopping condition
                stop_condition = generation > 10
                if stop_condition:
                    break
                # STUDENT Also consider using FI-2POP as in the Sorenson & Pasquier paper
                gentime = time.time()
                next_population = generate_successors(population)
                gendone = time.time()
                print("Generated successors in:", gendone - gentime, "seconds")
                # Calculate fitness in batches in parallel
                next_population = pool.map(Individual.calculate_fitness,
                                           next_population,
                                           batch_size)
                popdone = time.time()
                print("Calculated fitnesses in:", popdone - gendone, "seconds")
                population = next_population
        except KeyboardInterrupt:
            pass
    return population


if __name__ == "__main__":
    final_gen = sorted(ga(), key=Individual.fitness, reverse=True)
    best = final_gen[0]
    print("Best fitness: " + str(best.fitness()))
    now = time.strftime("%m_%d_%H_%M_%S")
    # STUDENT You can change this if you want to blast out the whole generation, or ten random samples, or...
    for k in range(0, 1):
        with open("levels/" + now + "_" + str(k) + ".txt", 'w') as f:
            for row in final_gen[k].to_level():
                f.write("".join(row) + "\n")
