import curses
from drawing_objects import draw


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
