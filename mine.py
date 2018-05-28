"""from https://github.com/mlotstein/StarFleet-Mine-Clearing-Exercise"""
import os.path
import re


def dist_to_char(distance):
    """
     * Convert the distance to the mine into a character
     * @param d
     * @return
    """
    if 1 <= distance <= 26:
        # in range a - z
        return chr(distance + 96)
    elif 26 <= distance <= 52:
        # in range A - Z
        return chr(distance + 38)
    return '*'


def char_to_z(char):
    """
     * Uses ASCII values to quickly convert characters to position in space.
     * @param c
     * @return
    """
    if 65 <= ord(char) <= 90:
        # in range A - Z
        return (-1) * (ord(char) - 38)
    # in range a - z
    return (-1) * (ord(char) - 96)


class Command(object):  # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    """Not so useful command key to command string mapping object"""
    ALPHA = None  # pylint: disable=invalid-name
    BETA = None  # pylint: disable=invalid-name
    GAMMA = None  # pylint: disable=invalid-name
    DELTA = None  # pylint: disable=invalid-name
    NORTH = None  # pylint: disable=invalid-name
    SOUTH = None  # pylint: disable=invalid-name
    EAST = None  # pylint: disable=invalid-name
    WEST = None  # pylint: disable=invalid-name
    WS = None  # pylint: disable=invalid-name

    def __init__(self):
        self.ALPHA = 'alpha'  # pylint: disable=invalid-name
        self.BETA = 'beta'  # pylint: disable=invalid-name
        self.GAMMA = 'gamma'  # pylint: disable=invalid-name
        self.DELTA = 'delta'  # pylint: disable=invalid-name
        self.NORTH = 'north'  # pylint: disable=invalid-name
        self.SOUTH = 'south'  # pylint: disable=invalid-name
        self.EAST = 'east'  # pylint: disable=invalid-name
        self.WEST = 'west'  # pylint: disable=invalid-name
        self.WS = ''  # pylint: disable=invalid-name


class Mission(object):  # pylint: disable=too-many-instance-attributes
    """Torpedo Mission processor"""
    activeMinesX = []
    activeMinesY = []
    activeMinesZ = []
    inactiveMinesX = []
    inactiveMinesY = []
    inactiveMinesZ = []
    ship_x, ship_y, ship_z, step_num = None, None, None, None

    shots_fired, move_commands, number_of_mines = None, None, 0
    field_file, script_file = None, None
    field_lines, script_lines = [], []
    steps = []
    command = None

    def __init__(self, field_file, script_file):
        """Initializes Mission object with field and script file names"""
        self.ship_x = 0
        self.ship_y = 0
        self.ship_z = 0
        self.shots_fired = 0
        self.move_commands = 0
        self.step_num = 1

        self.field_file, self.script_file = field_file, script_file
        self.command = Command()

    def transform_x(self, x_coor, max_x):
        """
         * Transforms a point in (0,0) coordinate system to one used by printMineField() function.
         * @param x
         * @param maxX
         * @return
        """
        return int(x_coor - (self.ship_x - max_x))

    def transform_y(self, y_coor, max_y):
        """
         * Transforms a point in (0,0) coordinate system to one used by print_mine_field() function.
         * @param y
         * @param maxY
         * @return
        """
        return int(y_coor - (self.ship_y - max_y))

    def print_mine_field(self):
        """Determine the minimum size of the grid s.t. the ship is in the center"""
        size_x = 0
        size_y = 0
        for mine_index in xrange(len(self.activeMinesX)):
            if abs(self.activeMinesX[mine_index]) > size_x:
                size_x = int(abs(self.activeMinesX[mine_index] - self.ship_x))
            if abs(self.activeMinesY[mine_index]) > size_y:
                size_y = int(abs(self.activeMinesY[mine_index] - self.ship_y))
        minefield = [['.' for _ in xrange(2 * size_x + 1)] for _ in xrange(2 * size_y + 1)]
        for mine_index in xrange(len(self.activeMinesX)):
            row = self.transform_y(self.activeMinesY[mine_index], size_y)
            col = self.transform_x(self.activeMinesX[mine_index], size_x)
            minefield[row][col] = dist_to_char(self.ship_z - int(self.activeMinesZ[mine_index]))
        for row in xrange(len(minefield)):
            print(''.join(minefield[row]))  # pylint: disable=superfluous-parens

    def add_mine(self, mine_x, mine_y, mine_z):
        """
        * Add another mine while maintaining condition that the activeMines variables
        * are always the same length.
        * @param x
        * @param y
        * @param z
        """
        self.activeMinesX.append(mine_x)
        self.activeMinesY.append(mine_y)
        self.activeMinesZ.append(mine_z)

    def parse_field(self):
        """Parses field's file into internal representation of travel space"""
        max_x, max_y = len(self.field_lines[0]), len(self.field_lines)
        if max_x % 2 == 0 or max_y % 2 == 0:
            print("Could not determine center of FieldFile")  # pylint: disable=superfluous-parens
            quit()
        origin_x, origin_y = round(max_x / 2), round(max_y / 2)
        self.ship_x, self.ship_y = origin_x, origin_y
        for field_line in xrange(len(self.field_lines)):
            line = self.field_lines[field_line]
            if len(line) != max_x:
                print("Found lines of different lengths in FieldFile")  # pylint: disable=superfluous-parens
                quit()
            for line_pointer in xrange(len(line)):
                if line[line_pointer] == '.':
                    # Found empty space
                    pass
                elif re.match("[a-zA-Z]", line[line_pointer:line_pointer + 1]):
                    self.add_mine(line_pointer, field_line, char_to_z(line[line_pointer]))
                    self.number_of_mines += 1
                else:
                    print("Found unexpected character in FieldFile")  # pylint: disable=superfluous-parens
                    quit()

    def print_command(self):
        """Prints list of commands on a script line from self.steps list"""
        print ' '.join(self.steps[self.step_num - 1])

    def parse_script(self):  # pylint: disable=too-many-branches
        """
         * Updates commands[] array to reflect contents of script file.
         * @param lines
         * @throws ParseException
        """
        self.steps = [[] for i in xrange(len(self.script_lines))]
        for i in xrange(len(self.script_lines)):
            if self.script_lines[i].strip() == '':
                self.steps.append(Command.WS)
            else:
                cur_steps = self.script_lines[i].split()
                if len(cur_steps) > 2:
                    print "Improperly formatted Script File: Too Many Commands On a Line %s" % i
                    quit()
                for step in cur_steps:
                    if step == 'alpha':
                        self.steps[i].append(self.command.ALPHA)
                    elif step == 'beta':
                        self.steps[i].append(self.command.BETA)
                    elif step == 'gamma':
                        self.steps[i].append(self.command.GAMMA)
                    elif step == 'delta':
                        self.steps[i].append(self.command.DELTA)
                    elif step == 'north':
                        self.steps[i].append(self.command.NORTH)
                    elif step == 'south':
                        self.steps[i].append(self.command.SOUTH)
                    elif step == 'east':
                        self.steps[i].append(self.command.EAST)
                    elif step == 'west':
                        self.steps[i].append(self.command.WEST)
                    else:
                        print "Unrecognized command in Script File line %s" % i

    def destroy_mine(self, mine_number):
        """
         * Deactivate a mine while maintaining condition that the activeMines variables
         * are always the same length.
         * @param mineNumber
        """
        mine_x = self.activeMinesX[mine_number]
        del (self.activeMinesX[mine_number])  # pylint: disable=superfluous-parens
        mine_y = self.activeMinesY[mine_number]
        del (self.activeMinesY[mine_number])  # pylint: disable=superfluous-parens
        mine_z = self.activeMinesZ[mine_number]
        del (self.activeMinesZ[mine_number])  # pylint: disable=superfluous-parens
        self.inactiveMinesX.append(mine_x)
        self.inactiveMinesY.append(mine_y)
        self.inactiveMinesZ.append(mine_z)

    def find_mines_on_xy_line(self, mine_x, mine_y):
        """
        * Find the indices of all mines on the line defined by x, y (where z can vary)
        * @return
        """
        mines = []
        for mine in xrange(len(self.activeMinesX)):
            if self.activeMinesX[mine] == mine_x and self.activeMinesY[mine] == mine_y:
                mines.append(mine)
        return mines

    def execute_command(self):  # pylint: disable=too-many-branches
        """First, fire photons and destroy mines as appropriate"""
        for step in self.steps[self.step_num - 1]:
            if step == self.command.ALPHA:
                mines_south_east = self.find_mines_on_xy_line(self.ship_x + 1, self.ship_y + 1)
                for mine in mines_south_east:
                    self.destroy_mine(mine)
                mines_north_east = self.find_mines_on_xy_line(self.ship_x + 1, self.ship_y - 1)
                for mine in mines_north_east:
                    self.destroy_mine(mine)
                mines_south_west = self.find_mines_on_xy_line(self.ship_x - 1, self.ship_y + 1)
                for mine in mines_south_west:
                    self.destroy_mine(mine)
                mines_north_west = self.find_mines_on_xy_line(self.ship_x - 1, self.ship_y - 1)
                for mine in mines_north_west:
                    self.destroy_mine(mine)
                self.shots_fired += 1
            elif step == self.command.BETA:
                mines_north = self.find_mines_on_xy_line(self.ship_x, self.ship_y - 1)
                for mine in mines_north:
                    self.destroy_mine(mine)
                mines_south = self.find_mines_on_xy_line(self.ship_x, self.ship_y + 1)
                for mine in mines_south:
                    self.destroy_mine(mine)
                mines_east = self.find_mines_on_xy_line(self.ship_x + 1, self.ship_y)
                for mine in mines_east:
                    self.destroy_mine(mine)
                mines_west = self.find_mines_on_xy_line(self.ship_x - 1, self.ship_y)
                for mine in mines_west:
                    self.destroy_mine(mine)
                self.shots_fired += 1
            elif step == self.command.GAMMA:
                mines_south_east = self.find_mines_on_xy_line(self.ship_x + 1, self.ship_y)
                for mine in mines_south_east:
                    self.destroy_mine(mine)
                mines_west = self.find_mines_on_xy_line(self.ship_x - 1, self.ship_y)
                for mine in mines_west:
                    self.destroy_mine(mine)
                mines_on_line = self.find_mines_on_xy_line(self.ship_x, self.ship_y)
                for mine in mines_on_line:
                    self.destroy_mine(mine)
                self.shots_fired += 1
            elif step == self.command.DELTA:
                mines_north = self.find_mines_on_xy_line(self.ship_x, self.ship_y - 1)
                for mine in mines_north:
                    self.destroy_mine(mine)
                mines_south = self.find_mines_on_xy_line(self.ship_x, self.ship_y + 1)
                for mine in mines_south:
                    self.destroy_mine(mine)
                mines_on_line = self.find_mines_on_xy_line(self.ship_x, self.ship_y)
                for mine in mines_on_line:
                    self.destroy_mine(mine)
                self.shots_fired += 1
            elif step == self.command.NORTH:
                self.ship_y -= 1
                self.move_commands += 1
            elif step == self.command.SOUTH:
                self.ship_y += 1
                self.move_commands += 1
            elif step == self.command.EAST:
                self.ship_x += 1
                self.move_commands += 1
            elif step == self.command.WEST:
                self.ship_x -= 1
                self.move_commands += 1
        # Always move down
        self.ship_z -= 1

    def has_past_mine(self):
        """
         * Returns true when there is an active mine with a Z coordinate
         * that is > current position. NOTE: Z position is always decremented after every step.
         * @return
        """
        for z_mine in self.activeMinesZ:
            if z_mine >= self.ship_z:
                return True
        return False

    def print_score(self):
        """Print score"""
        if self.has_past_mine():
            print "fail (0)"
        elif len(self.activeMinesX) > 0 and self.step_num == len(self.steps) + 1:  # pylint: disable=len-as-condition
            print "fail (0)"
        elif len(self.activeMinesX) == 0 and self.step_num == len(self.steps):  # pylint: disable=len-as-condition
            print "pass (1)"
        else:
            starting_score = self.number_of_mines * 10
            starting_score = starting_score - min(5 * self.number_of_mines, 5 * self.shots_fired)
            starting_score = starting_score - min(2 * self.move_commands, 3 * self.number_of_mines)
            print "pass (%s)" % starting_score

    def run(self):
        """The method that processes the inputs loaded in construction"""
        if os.path.exists(self.field_file):
            with open(self.field_file) as field_file:
                self.field_lines = field_file.readlines()
            # remove whitespace characters like `\n` at the end of each line
            self.field_lines = [x.strip() for x in self.field_lines]
        else:
            print("Error: file %s does not exist." % self.field_file)  # pylint: disable=superfluous-parens
            quit(1)
        if os.path.exists(self.script_file):
            with open(self.script_file) as script_file:
                self.script_lines = script_file.readlines()
            self.script_lines = [x.strip() for x in self.script_lines]
        else:
            print("Error: file %s does not exist." % self.script_file)  # pylint: disable=superfluous-parens
            quit(1)

        self.parse_field()
        self.parse_script()
        condition = True
        while condition:
            print("Step %s" % int(self.step_num))  # pylint: disable=superfluous-parens
            print("")  # pylint: disable=superfluous-parens
            self.print_mine_field()
            print("")  # pylint: disable=superfluous-parens
            self.print_command()
            self.execute_command()
            print("")  # pylint: disable=superfluous-parens
            self.print_mine_field()
            print("")  # pylint: disable=superfluous-parens
            self.step_num += 1
            # pylint: disable=len-as-condition
            condition = self.step_num <= len(self.steps) and len(
                self.activeMinesX) > 0 and self.has_past_mine() is False
        self.print_score()


MISSION_1 = Mission('test1.field', 'test1.script')

# MISSION_1.run()

MISSION_2 = Mission('test2.field', 'test2.script')

# MISSION_2.run()

MISSION_3 = Mission('test3.field', 'test3.script')

#MISSION_3.run()

MISSION_4 = Mission('test4.field', 'test4.script')

MISSION_4.run()

MISSION_5 = Mission('test5.field', 'test5.script')

#MISSION_5.run()
