import time
import curses
import asyncio
import curses
import random

TIC_TIMEOUT = 0.1


async def blink(canvas, row, column, symbol):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(2000):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_NORMAL)
        for _ in range(300):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(500):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(300):
            await asyncio.sleep(0)

async def animate_spaceship():
  pass

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


# def draw_firecanvas):
#     starts_cnt = 20
#     coroutines = []
#     canvas.border()
#     curses.curs_set(False)
#     print(canvas.getmaxyx())
#     for i in range(starts_cnt):
#         coroutines.append(
#             fire(canvas, random.randint(5,
#                                         canvas.getmaxyx()[0] - 5),
#                  random.randint(20,
#                                 canvas.getmaxyx()[1] - 20)
#                  #random.choice('+*.:')
#                  ))

#     while True:
#         if coroutines:
#             coroutine = coroutines[random.randint(0, len(coroutines) - 1)]
#         try:
#             coroutine.send(None)
#         except StopIteration:
#             coroutines.remove(coroutine)
#         if len(coroutines) == 0:
#             break
#         canvas.refresh()
#         time.sleep(0)
#     time.sleep(10)
      
def draw(canvas):
    starts_cnt = 20
    coroutines = []
    canvas.border()
    curses.curs_set(False)
    print(canvas.getmaxyx())
    for i in range(starts_cnt):
        coroutines.append(
            blink(
              canvas, 
              random.randint(
                5,
                canvas.getmaxyx()[0] - 5
              ),
              random.randint(
                20,
                canvas.getmaxyx()[1] - 20
              ),
              random.choice('+*.:')
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
        time.sleep(0)

    time.sleep(10)

if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
