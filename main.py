import asyncio
import curses
import random
import time
from itertools import cycle
from obstacles import Obstacle, show_obstacles, has_collision
from curses_tools import draw_frame, get_frame_size, read_controls
from physics import update_speed
from explosion import explode


TIC_TIMEOUT = 0.015
MIN_ROW = 10
MIN_COL = 20
BORDER = 1
STARS_CNT = 20
ROCKET_FRAMES = [
    'frames/rocket_frame_1.txt', 
    'frames/rocket_frame_2.txt'
]
GARBAGE_PATHS = [
    'frames/duck.txt', 
    'frames/hubble.txt',
    'frames/lamp.txt',
    'frames/trash_large.txt',
    'frames/trash_small.txt',
    'frames/trash_xl.txt'
]
GARBAGE_FRAMES = []
GAME_OVER='frames/game_over.txt'
COROUTINES = []
OBSTACLES = []
OBSTACLES_IN_LAST_COLLISIONS = []
YEAR = 1957
TICS_IN_ONE_YEAR = 50
PHRASES = {
    1957: "First Sputnik",
    1961: "Gagarin flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: "Take the plasma gun! Shoot the garbage!",
}


def get_garbage_delay_tics(year):
    if year < 1961:
        return None
    elif year < 1969:
        return 20 * 2
    elif year < 1981:
        return 14 * 2
    elif year < 1995:
        return 10 * 2
    elif year < 2010:
        return 8 * 2
    elif year < 2020:
        return 6 * 2
    else:
        return 2 * 2


async def increment_year():
    while True:
        await sleep(TICS_IN_ONE_YEAR)
        global YEAR
        YEAR += 1


def get_frame(filepath):
    with open(filepath, "r") as file:
        return file.read()
     

async def sleep(tics=1):
    if tics:
        for _ in range(tics):
            await asyncio.sleep(0)
    else:
        await asyncio.sleep(0)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """
    Animate garbage, flying from top to bottom. 
    Column position will stay same, as specified on start.
    """

    column = max(column, 0)
    column = min(column, MAX_SCREEN_X - 1)

    row_size, column_size = get_frame_size(garbage_frame)

    row = 0
    obstacle = Obstacle(
            row, column, row_size, column_size
    )
    OBSTACLES.append(
        obstacle
    )
    
    while row < MAX_SCREEN_Y:
        if obstacle in OBSTACLES_IN_LAST_COLLISIONS:
            OBSTACLES.remove(obstacle)
            OBSTACLES_IN_LAST_COLLISIONS.remove(obstacle)
            return

        obstacle.column = column
        obstacle.row = row
        draw_frame(canvas, row, column, garbage_frame)
        await sleep(2)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
    else:
        OBSTACLES.remove(obstacle)


async def fire(
    canvas,
    start_row,
    start_column,
    rows_speed=-0.3,
    columns_speed=0
):
    """
    Display animation of gun shot, direction and speed can be specified.
    """

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    max_row, max_column = MAX_SCREEN_Y - 1, MAX_SCREEN_X - 1

    curses.beep()
    
    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in OBSTACLES:
            if obstacle.has_collision(
                row, column
            ):
                await explode(canvas, row, column)
                OBSTACLES_IN_LAST_COLLISIONS.append(obstacle)
                return
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def show_gameover(canvas, gameover_frame):
    row_size, column_size = get_frame_size(gameover_frame)
    while True:
        draw_frame(
            canvas,
            MAX_SCREEN_Y / 2 - row_size/2,
            MAX_SCREEN_X / 2 - column_size/2,
            gameover_frame
        )
        await asyncio.sleep(0)


async def run_spaceship(canvas, row, column, frames, gameover_frame):
    """
    Rocket flame coroutine.
    Fire coroutine.
    Rocket control coroutine with speed processing.
    """
    row_size, col_size = get_frame_size(frames[0])
    row_speed, column_speed = 0, 0
    
    for frame in cycle(frames):
        rows_direction, columns_direction, space = read_controls(canvas)

        row_speed, column_speed = update_speed(
            row_speed=row_speed,
            column_speed=column_speed,
            rows_direction=rows_direction,
            columns_direction=columns_direction,
            row_speed_limit=5,
            column_speed_limit=5
        )

        new_row = row + rows_direction + row_speed
        new_column = column + columns_direction + column_speed

        if BORDER <= new_row <= MAX_SCREEN_X - row_size - BORDER:
            row = new_row
        if new_row >= MAX_SCREEN_X - row_size - BORDER:
            row = MAX_SCREEN_X - row_size - BORDER
        if new_row <= BORDER:
            row = BORDER

        if BORDER <= new_column <= MAX_SCREEN_X - col_size - BORDER:
            column = new_column
        if new_column >= MAX_SCREEN_X - col_size - BORDER:
            column = MAX_SCREEN_X - col_size - BORDER
        if new_column <= BORDER:
            column = BORDER

        # shooting animation coroutine
        if YEAR >= 2020 and space:
            COROUTINES.append(
                fire(
                    canvas,
                    start_row=row, 
                    start_column=column,
                )
            )
        draw_frame(canvas, row, column, frame)
        for obstacle in OBSTACLES:
            if obstacle.has_collision(
                row, column
            ):
                await show_gameover(canvas, gameover_frame)
                
        await sleep(1)
        draw_frame(
            canvas, row, column, frame, negative=True
        )


async def blink(canvas, row, column, symbol):
    """
    Star blinking coroutine.
    """
    star_freq = 5
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(5 * star_freq)
        canvas.addstr(row, column, symbol, curses.A_NORMAL)
        await sleep(1 * star_freq)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(3 * star_freq)
        canvas.addstr(row, column, symbol)
        await sleep(1 * star_freq)


async def fill_orbit_with_garbage(canvas):
    """
    Generate garbage coroutines.
    """
    while True:
        delay = get_garbage_delay_tics(YEAR)
        if delay:
            COROUTINES.append(
                fly_garbage(
                    canvas,
                    column=random.randint(
                        a=0,
                        b=MAX_SCREEN_X - 1
                    ),
                    garbage_frame=random.choice(GARBAGE_FRAMES)
                )
            )
            await sleep(delay) 
        else:
            await asyncio.sleep(0)


async def show_year(canvas):
    offset = 2
    while True:
        text = f'{YEAR}'
        if PHRASES.get(YEAR):
            text += f': {PHRASES.get(YEAR)}'
        draw_frame(canvas, offset, MAX_SCREEN_X - len(text) - offset, text)
        await asyncio.sleep(0)
        draw_frame(canvas, offset, MAX_SCREEN_X - len(text) - offset, text, negative=True)


def init_coroutines(canvas):
    # stars coroutines
    for _ in range(STARS_CNT):
        COROUTINES.append(
            blink(
                canvas, 
                random.randint(
                    0,
                    MAX_SCREEN_Y
                ),
                random.randint(
                    0,
                    MAX_SCREEN_X
                ),
                random.choice('+*.:')
            )
        )
    
    # garbage generating coroutine
    COROUTINES.append(fill_orbit_with_garbage(canvas))
    
    # rocket processing coroutine
    COROUTINES.append(
        run_spaceship(
            canvas, 
            MAX_SCREEN_Y / 2, 
            MAX_SCREEN_X / 2, 
            [get_frame(rocket_frame) for rocket_frame in ROCKET_FRAMES],
            get_frame(GAME_OVER)
        )
    )

    COROUTINES.append(show_year(canvas))
    COROUTINES.append(increment_year())


def draw(canvas):
    """
    Handmade event-loop.
    """
    curses.curs_set(False)
    canvas.nodelay(True)
    global MAX_SCREEN_X
    global MAX_SCREEN_Y
    MAX_SCREEN_Y, MAX_SCREEN_X = canvas.getmaxyx()
    # we should decrease virtual screen size to exclude cases, when random stars appear out of screen.
    # for screens with little dimensions
    MAX_SCREEN_Y, MAX_SCREEN_X = MAX_SCREEN_Y - 1, MAX_SCREEN_X - 1
    GARBAGE_FRAMES.extend([get_frame(x) for x in GARBAGE_PATHS])

    init_coroutines(canvas)

    while True:
        for coroutine in COROUTINES.copy():
            canvas.border()
            if not COROUTINES:
                break
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
        


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
