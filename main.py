import curses
import random
import time
import asyncio

from itertools import cycle
from curses_tools import draw_frame, read_controls, get_frame_size


TIC_TIMEOUT = 0.1
MIN_ROW = 10
MIN_COL = 20
BORDER = 1
STARS_CNT = 20
ROCKET_FRAMES = [
    'frames/rocket_frame_1.txt', 
    'frames/rocket_frame_2.txt'
]


def read_files(files):
    files_data = []
    for file in files:
        with open(file, "r") as my_file:
            files_data.append(my_file.read())
    return files_data


async def animate_spaceship(canvas, row, column, frames):
    row_size, col_size = get_frame_size(frames[0])
    max_row, max_col = canvas.getmaxyx()

    while True:
        for item in cycle(frames):
            rows_direction, cols_direction, space = read_controls(canvas)
            mod_row = row + rows_direction
            mod_column = column + cols_direction

            if BORDER <= mod_row <= max_row - row_size - BORDER:
                row = mod_row
            if BORDER <= mod_column <= max_col - col_size - BORDER:
                column = mod_column

            draw_frame(canvas, row, column, item)
            await asyncio.sleep(0)
            draw_frame(
                canvas, row, column, item, negative=True
            )

    
async def blink(canvas, row, column, symbol):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_NORMAL)
        for _ in range(1):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(1):
            await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    
    coroutines = []
    
    # stars coroutines
    for i in range(STARS_CNT):
        coroutines.append(
            blink(
                canvas, 
                random.randint(
                    0,
                    canvas.getmaxyx()[0] - 1
                ),
                random.randint(
                    0,
                    canvas.getmaxyx()[1] - 1
                ),
                random.choice('+*.:')
            )
        )
    # rocket coroutine
    coroutine_rocket = animate_spaceship(
        canvas, 
        canvas.getmaxyx()[0]/2, 
        canvas.getmaxyx()[1]/2, 
        read_files(
            ROCKET_FRAMES
        )
    )
    
    for corutine in coroutines:
        corutine.send(None)
        
    while True:
        canvas.border()
        if not coroutines:
            break
        
        try:
            coroutines[random.randint(0, STARS_CNT) - 1].send(None)
        except StopIteration:
            coroutines.remove(corutine)
        if len(coroutines) == 0:
            break
        coroutine_rocket.send(None)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()