import curses
import random
import time
import asyncio

from itertools import cycle
from curses_tools import draw_frame, read_controls, get_frame_size


TIC_TIMEOUT = 0.1
MIN_ROW = 10
MIN_COL = 20
BORDER = 5
ROCKET_FRAMES = [
    'frames/rocket_frame_1.txt', 
    'frames/rocket_frame_2.txt'
]
STARS_CNT = 20


async def animate_spaceship(canvas, row, column, frames):
    row_size, col_size = get_frame_size(frames[0])
    max_row, max_col = canvas.getmaxyx()
    min_row, min_col = (0,0)

    while True:
        for item in cycle(frames):
            rows_direction, cols_direction, space = read_controls(canvas)
            row += rows_direction
            column += cols_direction
            
            # fly down processing
            if row + rows_direction - BORDER>= max_row + row_size:
                row = min_row - row_size + BORDER
            # flight right processing
            if column + cols_direction - BORDER>= max_col + col_size:
                column = min_col - col_size + BORDER
            # fly up processing
            if row + rows_direction + BORDER<= min_row - row_size:
                row = max_row + row_size - BORDER
            # flight left processing
            if column + cols_direction + BORDER<= min_col - col_size:
                column = max_col + col_size - BORDER
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


async def fire(canvas,
               start_row,
               start_column,
               rows_speed=-0.3,
               columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def read_files(files):
    files_data = []
    for file in files:
        with open(file, "r") as my_file:
            files_data.append(my_file.read())
    return files_data


def draw_fire(canvas):
    starts_cnt = 20
    coroutines = []
    canvas.border()
    curses.curs_set(False)
    print(canvas.getmaxyx())
    for i in range(starts_cnt):
        coroutines.append(
            fire(
                canvas, 
                random.randint(
                    MIN_ROW,
                    canvas.getmaxyx()[0] - MIN_ROW
                ),
                random.randint(
                    MIN_COL,
                    canvas.getmaxyx()[1] - MIN_COL
                )
            )
        )
    
    while True:
        if coroutines:
            coroutine = coroutines[random.randint(0, len(coroutines) - 1)]
        try:
            coroutine.send(None)
        except StopIteration:
            coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        
    time.sleep(10)


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
  