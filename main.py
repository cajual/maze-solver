#!/usr/bin/env python

from random import *
from tkinter import *
from time import sleep


class Window:
    def __init__(self, width, height, title) -> None:
        self._root = Tk()
        self._root.title(title)
        self._root.geometry(f"{width}x{height}")
        self._root.protocol("WM_DELETE_WINDOW", self.close)
        self.canvas = Canvas(self._root, bg="white")
        self.canvas.pack(expand=1, fill="both")
        self.running = False

    def draw_line(self, line, color) -> None:
        line.draw(self.canvas, color)

    def redraw(self) -> None:
        self._root.update()
        self._root.update_idletasks()

    def wait_for_close(self) -> None:
        self.running = True
        while self.running is True:
            self.redraw()

    def close(self) -> None:
        self.running = False


class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y


class Line:
    def __init__(self, p1, p2) -> None:
        self.p1 = p1
        self.p2 = p2

    def draw(self, canvas, color) -> None:
        canvas.create_line(
            self.p1.x, self.p1.y, self.p2.x, self.p2.y, fill=color, width=2
        )
        canvas.pack(expand=1, fill="both")


class Cell:
    def __init__(self, p1, p2, win=None, visited=False) -> None:
        if (p1.x > p2.x) or (p1.y > p2.y):
            raise Exception("Invalid Coordinates")
        self.left_border = True
        self.right_border = True
        self.top_border = True
        self.bottom_border = True
        self.p1 = p1
        self.p2 = p2
        self._win = win
        self.visited = False

    def draw(self) -> None:
        if self._win is None:
            return
        if self.left_border:
            color = "black"
        else:
            color = "white"
        self._win.canvas.create_line(
            self.p1.x, self.p1.y, self.p1.x, self.p2.y, fill=color, width=2
        )
        if self.right_border:
            color = "black"
        else:
            color = "white"
        self._win.canvas.create_line(
            self.p2.x, self.p1.y, self.p2.x, self.p2.y, fill=color, width=2
        )
        if self.top_border:
            color = "black"
        else:
            color = "white"
        self._win.canvas.create_line(
            self.p1.x, self.p1.y, self.p2.x, self.p1.y, fill=color, width=2
        )
        if self.bottom_border:
            color = "black"
        else:
            color = "white"
        self._win.canvas.create_line(
            self.p1.x, self.p2.y, self.p2.x, self.p2.y, fill=color, width=2
        )

    def draw_move(self, to_cell, undo=False) -> None:
        color = "#ff0000" if undo == False else "#ffdddd"
        x = (self.p2.x - self.p1.x) // 2 + self.p1.x
        y = (self.p2.y - self.p1.y) // 2 + self.p1.y
        start = Point(x, y)
        x = (to_cell.p2.x - to_cell.p1.x) // 2 + to_cell.p1.x
        y = (to_cell.p2.y - to_cell.p1.y) // 2 + to_cell.p1.y
        end = Point(x, y)
        move = Line(start, end)
        self._win.draw_line(move, color)


class Maze:
    def __init__(
        self, x1, y1, num_rows, num_cols, cell_size_x, cell_size_y, win=None, seed=None
    ) -> None:
        self.win = win
        self.x1 = x1
        self.y1 = y1
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self.seed = seed(seed) if seed else None
        self._create_cells()

    def _create_cells(self) -> None:
        self._cells = []
        for x in range(
            self.x1, self.x1 + self.cell_size_x * self.num_cols, self.cell_size_x
        ):
            tmp_list = []
            for y in range(
                self.y1, self.y1 + self.cell_size_y * self.num_rows, self.cell_size_y
            ):
                tmp_p1 = Point(x, y)
                tmp_p2 = Point(x + self.cell_size_x, y + self.cell_size_y)
                tmp_cell = Cell(tmp_p1, tmp_p2, self.win)
                tmp_list.append(tmp_cell)
            self._cells.append(tmp_list)
        for i in range(len(self._cells)):
            for j in range(len(self._cells[i])):
                self._draw_cell(i, j)

    def _draw_cell(self, i, j) -> None:
        cell = self._cells[i][j]
        cell_x1 = (self.cell_size_x * i) + self.x1
        cell_x2 = cell_x1 + self.cell_size_x
        cell_y1 = (self.cell_size_y * j) + self.y1
        cell_y2 = cell_y1 + self.cell_size_y
        cell.draw()

    def _break_entrance_and_exit(self) -> None:
        self._cells[0][0].top_border = False
        self._draw_cell(0, 0)
        self._cells[-1][-1].bottom_border = False
        self._draw_cell(-1, -1)

    def _break_walls_r(self, i, j) -> None:
        self._cells[i][j].visited = True
        direction = {
            "left": self._cells[i - 1][j] if i > 0 else None,
            "right": self._cells[i + 1][j] if i < (self.num_cols - 1) else None,
            "up": self._cells[i][j - 1] if j > 0 else None,
            "down": self._cells[i][j + 1] if j < (self.num_rows - 1) else None,
        }
        while True:
            possible = []
            for k, v in direction.items():
                if v and v.visited == False:
                    possible.append(k)
            if len(possible) == 0:
                return
            vector = possible[randint(0, len(possible) - 1)]
            x, y = i, j
            if vector == "left":
                x -= 1
                self._cells[i][j].left_border = False
                self._cells[x][y].right_border = False
            if vector == "right":
                x += 1
                self._cells[i][j].right_border = False
                self._cells[x][y].left_border = False
            if vector == "up":
                y -= 1
                self._cells[i][j].top_border = False
                self._cells[x][y].bottom_border = False
            if vector == "down":
                y += 1
                self._cells[i][j].bottom_border = False
                self._cells[x][y].top_border = False
            self._cells[i][j].draw()
            self._break_walls_r(x, y)

    def _reset_cells_visted(self) -> None:
        for i in self._cells:
            for j in i:
                j.visited = False

    def solve(self) -> bool:
        if self._solve_r(0, 0):
            return True
        return False

    def _solve_r(self, i, j) -> bool:
        c = self._cells[i][j]
        subx = self.cell_size_x // 2
        suby = self.cell_size_y // 2
        c.visited = True
        if i == len(self._cells) - 1 and j == len(self._cells[0]) - 1:
            return True
        directions = []
        if c.top_border == False and j > 0 and self._cells[i][j - 1].visited == False:
            directions.append(["up", 0, -1])
        if (
            c.right_border == False
            and i < len(self._cells[0]) - 1
            and self._cells[i + 1][j].visited == False
        ):
            directions.append(["right", 1, 0])
        if (
            c.bottom_border == False
            and j < len(self._cells) - 1
            and self._cells[i][j + 1].visited == False
        ):
            directions.append(["down", 0, 1])
        if c.left_border == False and i > 0 and self._cells[i - 1][j].visited == False:
            directions.append(["left", -1, 0])
        if len(directions) < 1:
            return False
        for direction in directions:
            c.draw_move(self._cells[i + direction[1]][j + direction[2]])
            if self._solve_r(i + direction[1], j + direction[2]):
                return True
            c.draw_move(self._cells[i + direction[1]][j + direction[2]], True)

    def _animate(self, time) -> None:
        self.win.redraw()
        sleep(time)


def main():
    window = Window("1000", "1000", "Maze Solver")

    ## Test
    maze = Maze(25, 25, 38, 38, 25, 25, window)
    maze._break_entrance_and_exit()
    maze._break_walls_r(0, 0)
    maze._reset_cells_visted()
    maze.solve()
    ##

    window.wait_for_close()


if __name__ == "__main__":
    main()
