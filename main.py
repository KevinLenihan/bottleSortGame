

import arcade
import arcade.gui
import random
import tinytree
import copy

SCREEN_WIDTH = 650
SCREEN_HEIGHT = 600

BOTTLE_HEIGHT_COUNT = 4
BOTTLE_RENDER_HEIGHT = 25
BOTTLE_RENDER_WIDTH = 40
BOTTLE_SPACING = 20
BOTTLE_BORDER = 3
BOTTLE_ROW_COUNT = 7
SELECTED_BUMP = 10
HINT_FONT_SIZE = 10

BOTTLE_START_X = 50
BOTTLE_START_Y = 340


BACKGROUND_COLOR = arcade.color.WHITE_SMOKE

COLORS = [
        BACKGROUND_COLOR,
        arcade.color.RED,
        arcade.color.BLUE,
        arcade.color.GREEN,
        arcade.color.PURPLE,
        arcade.color.ORANGE,
        arcade.color.YELLOW,
        arcade.color.PINK,
        arcade.color.BARN_RED,
        arcade.color.AMAZON,
        arcade.color.BABY_BLUE,
        arcade.color.BATTLESHIP_GREY,
        arcade.color.ANDROID_GREEN
    ]


def dtoa(num):
    alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return alpha[num]


class GameRenderer:
    @staticmethod
    def get_bottle_position(bottle):
        # TODO: this is incomplete. May not even make sense to have this here

        shift_x = (bottle.id % BOTTLE_ROW_COUNT)
        shift_y = (bottle.id // BOTTLE_ROW_COUNT)

        x = BOTTLE_START_X + shift_x - BOTTLE_RENDER_WIDTH / 2 - 1
        y = BOTTLE_START_Y + shift_y - BOTTLE_RENDER_HEIGHT / 2
        width = 10
        height = 10

        return x, y, width, height

    @staticmethod
    def render_bottles(gm):
        cur_x = BOTTLE_START_X
        cur_y = BOTTLE_START_Y
        row = 0
        b_count = 0
        bottles = gm.get_bottles()
        show_hints = gm.show_hints()

        for bottle in bottles:
            selected_bump = 0
            if bottle.is_selected():
                selected_bump = SELECTED_BUMP
            sections = bottle.get_contents()
            bottle.x = cur_x - BOTTLE_RENDER_WIDTH / 2 - 1
            bottle.y = cur_y - BOTTLE_RENDER_HEIGHT / 2
            bottle.width = BOTTLE_RENDER_WIDTH

            actual_x = cur_x
            actual_y = cur_y + selected_bump

            arcade.draw_rectangle_filled(
                actual_x - .25, actual_y - BOTTLE_RENDER_HEIGHT / 2 - 2, BOTTLE_RENDER_WIDTH + 6, BOTTLE_BORDER,
                arcade.color.BLACK)

            arcade.draw_text(bottle.get_name(), cur_x - BOTTLE_RENDER_WIDTH / 2 - 1,
                             cur_y - BOTTLE_RENDER_HEIGHT / 2 - BOTTLE_SPACING, arcade.color.BLACK, HINT_FONT_SIZE,
                             width=BOTTLE_RENDER_WIDTH, align="center",bold=True)

            i = 1
            while i <= bottle.height_count:
                if len(sections) >= i:
                    section = COLORS[sections[-1 * i]]
                else:
                    section = COLORS[0]  # NULL COLOR currently white

                actual_x = cur_x
                actual_y = cur_y + selected_bump

                arcade.draw_rectangle_filled(
                    actual_x - BOTTLE_RENDER_WIDTH / 2 - 1, actual_y, BOTTLE_BORDER, BOTTLE_RENDER_HEIGHT, arcade.color.BLACK)
                arcade.draw_rectangle_filled(
                    actual_x + BOTTLE_RENDER_WIDTH / 2 + 2, actual_y, BOTTLE_BORDER, BOTTLE_RENDER_HEIGHT, arcade.color.BLACK)
                arcade.draw_rectangle_filled(actual_x, actual_y, BOTTLE_RENDER_WIDTH, BOTTLE_RENDER_HEIGHT, section)

                cur_y += BOTTLE_RENDER_HEIGHT
                if i is bottle.height_count:
                    if show_hints:
                        moves = ' '.join(bottle.find_moves(bottles, alpha=True))

                        arcade.draw_text(moves, actual_x - BOTTLE_RENDER_WIDTH / 2,
                                         actual_y - BOTTLE_RENDER_HEIGHT / 2 + HINT_FONT_SIZE, arcade.color.BLACK,
                                         HINT_FONT_SIZE, width=BOTTLE_RENDER_WIDTH, align="center", bold=True)

                    bottle.height = (cur_y + BOTTLE_RENDER_HEIGHT/2) - bottle.y
                i += 1

            b_count += 1
            if b_count is BOTTLE_ROW_COUNT:
                row += 1
                b_count = 0
                cur_x = BOTTLE_START_X
            else:
                cur_x += BOTTLE_RENDER_WIDTH + BOTTLE_SPACING
            cur_y = BOTTLE_START_Y - (row * (BOTTLE_RENDER_HEIGHT * BOTTLE_HEIGHT_COUNT + 2 * BOTTLE_SPACING))


class GameManager:
    def __init__(self, bottle_count):
        self.bottles = []
        self.tree_root = SavedState("Root")
        self.cur_state = self.tree_root
        self.hints = False
        self.bottle_count = bottle_count

        for i in range(self.bottle_count):
            self.add_bottle(Bottle(color=i+1, bottle_id=i))

    def get_bottles(self):
        return self.bottles

    def show_hints(self):
        return self.hints

    def is_solved(self):
        for bottle in self.bottles:
            depth = bottle.get_pour_depth()
            if depth != bottle.height_count and depth != 0:
                return False
        return True

    def setup(self):
        self.shuffle_bottles()
        self.add_bottle(Bottle(False, len(self.bottles)))
        self.add_bottle(Bottle(False, len(self.bottles)))
        self.save_state()

    def add_bottle(self, bottle):
        self.bottles.append(bottle)

    def shuffle_bottles(self):
        pile = []
        for bottle in self.bottles:
            sections = bottle.get_contents()
            for section in sections:
                pile.append(section)
        random.shuffle(pile)
        for bottle in self.bottles:
            sections = []
            for i in range(BOTTLE_HEIGHT_COUNT):
                sections.append(pile.pop())
            bottle.set_contents(sections)

    def save_state(self):
        print("Saving")
        old_bottles = copy.deepcopy(self.bottles)
        child = SavedState(old_bottles)
        self.cur_state.addChild(child)
        self.cur_state = child

    def get_prev_state(self):
        ret = self.cur_state.parent
        if ret.parent is None:
            return False
        return ret

    def get_start_state(self):
        return self.tree_root.getNext()

    def start_new_game(self):
        self.bottles = []
        self.tree_root = SavedState("Root")
        self.cur_state = self.tree_root
        self.hints = False

        for i in range(self.bottle_count):
            self.add_bottle(Bottle(color=i+1, bottle_id=i))
        self.setup()

    def show_moves(self):
        self.hints = not self.hints

    def set_current_state(self, state):
        if not state:
            return
        self.cur_state = state
        new_bottles = copy.deepcopy(self.cur_state.get_game_state())
        self.bottles = new_bottles
        for bottle in self.bottles:
            bottle.set_selected(False)

        print("cur state:" + str(self.cur_state.getDepth()))
        self.print_tree()

    def print_tree(self):
        self.tree_root.print_tree()


class Bottle:
    def __init__(self, color=False, bottle_id=0):
        self.height_count = BOTTLE_HEIGHT_COUNT
        self.contents = []
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.id = bottle_id
        self.selected = False
        self.moves = []
        self.moves_names = []
        if color:
            for x in range(self.height_count):
                self.contents.append(color)

    def fill(self, bottle):
        if self.can_fill(bottle):
            pour_depth = self.get_pour_depth()
            space_avail = bottle.height_count - bottle.get_filled_height()
            if space_avail < pour_depth:
                pour_depth = space_avail
            for i in range(pour_depth):
                bottle.contents.append(self.pop())

    def can_fill(self, bottle):
        pouring_color = self.get_top_color()

        receiving_color = bottle.get_top_color()
        if receiving_color is not False:
            if pouring_color is not receiving_color or bottle.get_filled_height() is bottle.height_count:
                return False
        return True

    def find_moves(self, bottles, alpha=False):
        self.moves = []
        self.moves_names = []

        if self.get_filled_height() > 0:
            for bottle in bottles:
                if bottle.id is not self.id and self.can_fill(bottle):
                    self.moves.append(bottle.id)
                    self.moves_names.append(bottle.get_name())
        if alpha:
            return self.moves_names
        return self.moves

    def get_moves(self, alpha=False):
        if alpha:
            return self.moves_names
        return self.moves

    def get_name(self):
        return dtoa(self.id)

    def get_pour_depth(self):
        if self.get_filled_height() == 0:
            return 0
        color = self.get_top_color()
        depth = 1
        while len(self.contents) > depth:
            if self.contents[-1 * (depth + 1)] is color:
                depth += 1
            else:
                return depth
        return depth

    def is_selected(self):
        return self.selected

    def set_selected(self, status):
        self.selected = status

    def is_click_in_bottle(self, x, y):
        if self.x < x < self.x + self.width and self.y < y < self.y + self.height:
            return True
        return False

    def pop(self):
        return self.contents.pop()

    def get_filled_height(self):
        return len(self.contents)

    def get_top_color(self):
        if self.get_filled_height() > 0:
            return self.contents[-1]
        return False

    def get_contents(self):
        ret = []
        for i in range(self.get_filled_height() - 1, -1, -1):
            ret.append(self.contents[i])
        return ret

    def set_contents(self, contents):
        self.contents = contents


class SavedState(tinytree.Tree):
    def __init__(self, game_state):
        super().__init__()
        self.game_state = game_state

    def set_game_state(self, game_state):
        self.game_state = game_state

    def get_game_state(self):
        return self.game_state

    def print_tree(self):
        print(self.getDepth())
        if self.children:
            for child in self.children:
                child.print_tree()


class VialSort(arcade.Window):

    def __init__(self, bottle_count):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT)

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        arcade.set_background_color(BACKGROUND_COLOR)
        self.gr = GameRenderer()
        self.gm = GameManager(bottle_count)
        self.selected = False
        self.v_box = arcade.gui.UIBoxLayout(vertical=False, space_between=10)

        undo_button = arcade.gui.UIFlatButton(text="Undo", width=100)
        undo_button.on_click = lambda x: self.gm.set_current_state(self.gm.get_prev_state())
        self.v_box.add(undo_button)

        reset_button = arcade.gui.UIFlatButton(text="Reset", width=100)
        reset_button.on_click = lambda x: self.gm.set_current_state(self.gm.get_start_state())
        self.v_box.add(reset_button)

        hint_button = arcade.gui.UIFlatButton(text="Hint", width=100)
        hint_button.on_click = lambda x: self.gm.set_current_state(self.gm.show_moves())
        self.v_box.add(hint_button)

        new_game_button = arcade.gui.UIFlatButton(text="New Game", width=100)
        self.v_box.add(new_game_button)
        new_game_button.on_click = lambda x: self.gm.start_new_game()

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="left",
                anchor_y="top",
                child=self.v_box)
        )

        self.gm.setup()

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        self.manager.draw()

        self.gr.render_bottles(self.gm)

    def update(self, delta_time):
        """ All the logic to move, and the game logic goes here. """
        if self.gm.is_solved():
            print("Hooray")

    def on_mouse_press(self, x, y, button, modifiers):
        print("Mouse button is pressed :" + str(x) + "," + str(y))
        for bottle in self.gm.get_bottles():
            if bottle.is_click_in_bottle(x, y):
                print(bottle.id)
                if not self.selected:
                    if bottle.get_filled_height() == 0:
                        break
                    self.selected = bottle
                    bottle.set_selected(True)
                else:
                    ret = self.selected.fill(bottle)
                    self.selected.set_selected(False)
                    self.selected = False
                    if ret:
                        self.gm.save_state()
                break

    def is_click_in_bottle(self, x, y):
        if self.x < x < self.x + self.width and self.y < y < self.y + self.height:
            return True
        return False


def main():
    game = VialSort(12)
    arcade.run()


if __name__ == "__main__":
    main()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
