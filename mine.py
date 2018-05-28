"""from https://github.com/mlotstein/StarFleet-Mine-Clearing-Exercise"""
import os.path
import re

"""
 * Uses ASCII values to quickly convert characters to position in space.
 * @param c
 * @return
"""


def char_to_z(c):
    if 65 <= ord(c) <= 90:
        # in range A - Z
        return (-1) * (ord(c) - 38)
    else:
        # in range a - z
        return (-1) * (ord(c) - 96)

"""
 * Find the indices of all mines on the line defined by x, y (where z can vary)
 * @return
"""

class Command:

    ALPHA = None
    BETA = None
    GAMMA = None
    DELTA = None
    NORTH = None
    SOUTH = None
    EAST = None
    WEST = None
    WS = None

    def __init__(self):
        self.ALPHA = 'alpha'
        self.BETA = 'beta'
        self.GAMMA = 'gamma'
        self.DELTA = 'delta'
        self.NORTH = 'north'
        self.SOUTH = 'south'
        self.EAST = 'east'
        self.WEST = 'west'
        self.WS = ''


class Mission:

    activeMinesX = []
    activeMinesY = []
    activeMinesZ = []
    inactiveMinesX = []
    inactiveMinesY = []
    inactiveMinesZ = []
    shipX, shipY, shipZ, stepNum = None, None, None, None

    shotsFired, moveCMDs, numMines = None, None, 0
    fieldFile, scriptFile = None, None
    fieldLines, scriptLines = [], []
    steps = []
    command = None

    def __init__(self, fieldFile, scriptFile):

        self.shipX = 0
        self.shipY = 0
        self.shipZ = 0
        self.shotsFired = 0
        self.moveCMDs = 0
        self.stepNum = 1

        self.fieldFile, self.scriptFile = fieldFile, scriptFile
        self.Command = Command()

    """
     * Transforms a point in (0,0) coordinate system to one used by printMineField() function.
     * @param x
     * @param maxX
     * @return
    """
    def transform_x(self, x, max_x):
        return int(x - (self.shipX - max_x))


    """
     * Transforms a point in (0,0) coordinate system to one used by print_mine_field() function.
     * @param y
     * @param maxY
     * @return
    """
    def transform_y(self, y, max_y):
        return int(y - (self.shipY - max_y))

    """
     * Convert the distance to the mine into a character
     * @param d
     * @return
    """
    def dist_to_char(self, d):
        if 1 <= d <= 26:
            # in range a - z
            return chr(d + 96)
        elif 26 <= d <= 52:
            # in range A - Z
            return chr(d + 38)
        else:
            return '*'

    def print_mine_field(self):
        # Determine the minimum size of the grid s.t. the ship is in the center
        sizeX = 0
        sizeY = 0
        for m in xrange(len(self.activeMinesX)):
            if abs(self.activeMinesX[m]) > sizeX:
                sizeX = int(abs(self.activeMinesX[m] - self.shipX))
            if abs(self.activeMinesY[m]) > sizeY:
                sizeY = int(abs(self.activeMinesY[m] - self.shipY))
        minefield = [['.' for _ in xrange(2*sizeX + 1)] for _ in xrange(2*sizeY + 1)]
        for m in xrange(len(self.activeMinesX)):
            row = self.transform_y(self.activeMinesY[m], sizeY)
            col = self.transform_x(self.activeMinesX[m], sizeX)
            minefield[row][col] = self.dist_to_char(self.shipZ - int(self.activeMinesZ[m]))
        for r in xrange(len(minefield)):
            print(''.join(minefield[r]))

    def add_mine(self, x, y, z):
        self.activeMinesX.append(x)
        self.activeMinesY.append(y)
        self.activeMinesZ.append(z)

    def parse_field(self):
        max_x, max_y = len(self.fieldLines[0]), len(self.fieldLines)
        if max_x % 2 == 0 or max_y % 2 == 0:
            print("Could not determine center of FieldFile")
            quit()
        origin_x, origin_y = round(max_x/2), round(max_y/2)
        self.shipX, self.shipY = origin_x, origin_y
        for l in xrange(len(self.fieldLines)):
            line = self.fieldLines[l]
            if len(line) != max_x:
                print("Found lines of different lengths in FieldFile");
                quit()
            for c in xrange(len(line)):
                if line[c] == '.':
                    # Found empty space
                    pass
                elif re.match("[a-zA-Z]", line[c:c+1]):
                    self.add_mine(c, l, char_to_z(line[c]))
                    self.numMines += 1
                else:
                    print("Found unexpected character in FieldFile")
                    quit()

    def print_command(self):
        print ' '.join(self.steps[self.stepNum - 1])

    """
     * Updates commands[] array to reflect contents of script file.
     * @param lines
     * @throws ParseException
    """
    def parse_script(self):
        self.steps = [[] for i in xrange(len(self.scriptLines))]
        for i in xrange(len(self.scriptLines)):
            if self.scriptLines[i].strip() == '':
                self.steps.append(Command.WS)
            else:
                cur_steps = self.scriptLines[i].split()
                if len(cur_steps) > 2:
                    print "Improperly formatted Script File: Too Many Commands On a Line %s" % i
                    quit()
                for s in cur_steps:
                    if s == 'alpha':
                        self.steps[i].append(self.Command.ALPHA)
                    elif s == 'beta':
                        self.steps[i].append(self.Command.BETA)
                    elif s == 'gamma':
                        self.steps[i].append(self.Command.GAMMA)
                    elif s == 'delta':
                        self.steps[i].append(self.Command.DELTA)
                    elif s == 'north':
                        self.steps[i].append(self.Command.NORTH)
                    elif s == 'south':
                        self.steps[i].append(self.Command.SOUTH)
                    elif s == 'east':
                        self.steps[i].append(self.Command.EAST)
                    elif s == 'west':
                        self.steps[i].append(self.Command.WEST)
                    else:
                        print "Unrecognized command in Script File line %s" % i

    """
     * Deactivate a mine while maintaining condition that the activeMines variables are always the same length.
     * @param mineNumber
    """
    def destroy_mine(self, mine_number):
        x = self.activeMinesX[mine_number]
        del(self.activeMinesX[mine_number])
        y = self.activeMinesY[mine_number]
        del(self.activeMinesY[mine_number])
        z = self.activeMinesZ[mine_number]
        del(self.activeMinesZ[mine_number])
        self.inactiveMinesX.append(x)
        self.inactiveMinesY.append(y)
        self.inactiveMinesZ.append(z)

    def find_mines_on_xy_line(self, x, y):
        mines = []
        for m in xrange(len(self.activeMinesX)):
            if self.activeMinesX[m] == x and self.activeMinesY[m] == y:
                mines.append(m);
        return mines

    def execute_command(self):
        # First, fire photons and destroy mines as appropriate
        for c in self.steps[self.stepNum - 1]:
            if c == self.Command.ALPHA:
                mines_south_east = findMinesOnXYLine(self.shipX + 1, self.shipY + 1)
                for m in mines_south_east:
                    self.destroy_mine(m)
                mines_north_east = findMinesOnXYLine(self.shipX + 1, self.shipY - 1)
                for m in mines_north_east:
                    self.destroy_mine(m)
                mines_south_west = findMinesOnXYLine(self.shipX - 1, self.shipY + 1)
                for m in mines_south_west:
                    self.destroy_mine(m)
                mines_north_west = findMinesOnXYLine(self.shipX - 1, self.shipY - 1)
                for m in mines_north_west:
                    self.destroy_mine(m)
                self.shotsFired += 1
            elif c == self.Command.BETA:
                mines_north = self.find_mines_on_xy_line(self.shipX, self.shipY - 1)
                for m in mines_north:
                    self.destroy_mine(m)
                mines_south = find_mines_on_xy_line(self.shipX, self.shipY + 1)
                for m in mines_south:
                    self.destroy_mine(m)
                mines_east = find_mines_on_xy_line(self.shipX + 1, self.shipY)
                for m in mines_east:
                    self.destroy_mine(m)
                mines_west = find_mines_on_xy_line(shipX - 1, shipY)
                for m in mines_west:
                    self.destroy_mine(m)
                self.shotsFired += 1
            elif c == self.Command.GAMMA:
                mines_south_east = self.find_mines_on_xy_line(self.shipX + 1, self.shipY)
                for m in mines_south_east:
                    self.destroy_mine(m)
                mines_west = self.find_mines_on_xy_line(self.shipX - 1, self.shipY)
                for m in mines_west:
                    self.destroy_mine(m)
                mines_on_line = self.find_mines_on_xy_line(self.shipX, self.shipY)
                for m in mines_on_line:
                    self.destroy_mine(m)
                self.shotsFired += 1
            elif c == self.Command.DELTA:
                mines_north = self.find_mines_on_xy_line(self.shipX, self.shipY - 1)
                for m in mines_north:
                    self.destroy_mine(m)
                mines_south = self.find_mines_on_xy_line(self.shipX, self.shipY + 1)
                for m in mines_south:
                    self.destroy_mine(m)
                mines_on_line = self.find_mines_on_xy_line(self.shipX, self.shipY)
                for m in mines_on_line:
                    self.destroy_mine(m)
                self.shotsFired += 1
            elif c == self.Command.NORTH:
                self.shipY -= 1
                self.moveCMDs += 1
            elif c == self.Command.SOUTH:
                self.shipY += 1
                self.moveCMDs += 1
            elif c == self.Command.EAST:
                self.shipX += 1
                self.moveCMDs += 1
            elif c == self.Command.WEST:
                self.shipX -= 1
                self.moveCMDs += 1
        # Always move down
        self.shipZ -= 1

    """
     * Returns true when there is an active mine with a Z coordinate
     * that is > current position. NOTE: Z position is always decremented after every step.
     * @return
    """
    def has_past_mine(self):
        for z in self.activeMinesZ:
            if z >= self.shipZ:
                return True
        return False

    def print_score(self):
        if self.has_past_mine():
            print "fail (0)"
        elif len(self.activeMinesX) > 0 and self.stepNum == len(self.steps) + 1:
            print "fail (0)"
        elif len(self.activeMinesX) == 0 and self.stepNum == len(self.steps):
            print "pass (1)"
        else:
            startingScore = self.numMines * 10;
            startingScore = startingScore - min(5 * self.numMines, 5 * self.shotsFired);
            startingScore = startingScore - min(2 * self.moveCMDs, 3 * self.numMines);
            print "pass (%s)" % startingScore

    def run(self):
        if os.path.exists(self.fieldFile):
            with open(self.fieldFile) as f:
                self.fieldLines = f.readlines()
            # remove whitespace characters like `\n` at the end of each line
            self.fieldLines = [x.strip() for x in self.fieldLines]
        else:
            print("Error: file %s does not exist." % self.fieldFile)
            quit(1)
        if os.path.exists(self.scriptFile):
            with open(self.scriptFile) as f:
                self.scriptLines = f.readlines()
            self.scriptLines = [x.strip() for x in self.scriptLines]
        else:
            print("Error: file %s does not exist." % self.scriptFile)
            quit(1)

        self.parse_field()
        self.parse_script()
        condition = True
        while condition:

            print("Step %s" % int(self.stepNum))
            print("")
            self.print_mine_field()
            print("")
            self.print_command()
            self.execute_command()
            print("")
            self.print_mine_field()
            print("")
            self.stepNum += 1
            condition = self.stepNum <= len(self.steps) and len(self.activeMinesX) > 0 and self.has_past_mine() is False
        self.print_score()

mission = Mission('test1.field', 'test1.script')

#mission.run()

mission2 = Mission('test2.field', 'test2.script')

#mission2.run()

mission3 = Mission('test3.field', 'test3.script')

#mission3.run()


mission4 = Mission('test4.field', 'test4.script')

#mission4.run()

mission5 = Mission('test5.field', 'test5.script')

mission5.run()
