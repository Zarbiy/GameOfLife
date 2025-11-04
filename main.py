from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QLabel, QPushButton, QGraphicsRectItem, QFileDialog
from PyQt6.QtGui import QBrush, QColor, QPainter
from PyQt6.QtCore import Qt, QTimer

import sys

from collections import Counter

colors = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "LIGHT_GREEN": (144, 238, 144),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "CYAN": (0, 255, 255),
    "MAGENTA": (255, 0, 255),
    "ORANGE": (255, 165, 0),
    "PURPLE": (128, 0, 128),
    "PINK": (255, 192, 203),
    "GREY": (128, 128, 128),
    "LIGHT_GREY": (200, 200, 200),
    "DARK_GREY": (50, 50, 50),
    "BROWN": (139, 69, 19),
    "LIGHT_BLUE": (173, 216, 230),
    "DARK_GREEN": (0, 100, 0)
}

class MainWindow(QGraphicsView):
    def __init__(self, n_cell_to_stay_alive = [2, 3], n_cell_to_birth = 3, interval = 500):
        super().__init__()
        self.setWindowTitle("Life is a game")
        self.resize(1000, 1000)

        self.cell_size = 40
        self.cam_x = 0
        self.cam_y = 0

        self.interval = interval
        self.speed_factor = 1.0
        self.key_press = {"s_press": False,
                          "a_press": False}
        
        self.running = False
        self.show_grid = True

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.alive_cells = set()
        self.nb_stay_alive = n_cell_to_stay_alive
        self.nb_become_alive = n_cell_to_birth

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(self.DragMode.ScrollHandDrag)

        self.last_mouse_pos = None
        self.setMouseTracking(True)

        self.pause_button = QPushButton("Play", self)
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.setGeometry(25, 25, 120, 50)

        self.reset_cell = QPushButton("Clear", self)
        self.reset_cell.clicked.connect(self.reset)
        self.reset_cell.setGeometry(25, 75, 120, 50)

        self.import_button = QPushButton("Import pattern", self)
        self.import_button.clicked.connect(self.import_pattern)
        self.import_button.setGeometry(25, 125, 120, 50)

        self.grid_button = QPushButton("Remove grid", self)
        self.grid_button.clicked.connect(self.action_grid)
        self.grid_button.setGeometry(25, 175, 120, 50)

        self.speed_up_btn = QPushButton("+", self)
        self.speed_up_btn.setGeometry(50, 160, 45, 45)
        self.speed_up_btn.clicked.connect(self.increase_speed)

        self.speed_down_btn = QPushButton("-", self)
        self.speed_down_btn.setGeometry(105, 160, 45, 45)
        self.speed_down_btn.clicked.connect(self.decrease_speed)

        self.speed_label = QLabel(f"Speed: {self.speed_factor}x", self)
        self.speed_label.setGeometry(50, 210, 100, 30)
        self.speed_label.setStyleSheet("color: white; background-color: rgba(0,0,0,0.5); padding: 3px;")

        margin = 50
        self.speed_up_btn.move(self.width() - self.speed_up_btn.width() - margin, margin)
        self.speed_down_btn.move(self.width() - self.speed_down_btn.width() * 2 - margin - 5, margin)
        self.speed_label.move(self.width() - self.speed_label.width() - margin, self.speed_up_btn.height() + margin + 5)

        self.pop_label = QLabel(self)
        self.pop_label.setStyleSheet("background-color: rgba(0,0,0,0.5); color: white; padding: 3px; border-radius: 5px;")
        self.pop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pop_label.setText("Pop: 0")
        self.pop_label.adjustSize()

        self.pop_label.move(5, self.height() - self.pop_label.height() - 15)

        self.draw_grid()

        self.timer = QTimer()
        self.timer.setInterval(int(self.interval / self.speed_factor))
        self.timer.timeout.connect(self.update_grid)

    def increase_speed(self):
        self.speed_factor = min(20, self.speed_factor + 0.5)
        self.timer.setInterval(int(self.interval / self.speed_factor))
        self.update_speed_label()

    def decrease_speed(self):
        self.speed_factor = max(0.5, self.speed_factor - 0.5)
        self.timer.setInterval(int(self.interval / self.speed_factor))
        self.update_speed_label()

    def update_speed_label(self):
        self.speed_label.setText(f"Speed: {self.speed_factor}x")

    def update_pop_label(self):
        self.pop_label.setText(f"Pop: {len(self.alive_cells)}")
        self.pop_label.adjustSize()

    def reset(self):
        self.alive_cells = set()
        self.update_pop_label()
        if not self.running:
            self.draw_grid()

    def toggle_pause(self):
        if self.running:
            self.timer.stop()
            self.pause_button.setText("Play")
        else:
            self.timer.start(int(self.interval / self.speed_factor))
            self.pause_button.setText("Pause")
        self.running = not self.running

    def action_grid(self):
        if self.show_grid:
            self.grid_button.setText("Show grid")
        else:
            self.grid_button.setText("Remove grid")
        self.show_grid = not self.show_grid
        self.draw_grid()


    def import_pattern(self):
        if self.running:
            print("Pause game to import file")
            return

        filename, _ = QFileDialog.getOpenFileName(self, "Import pattern", "", "Text Files (*.txt)")
        if not filename:
            return

        try:
            with open(filename, "r") as f:
                lines = [l.strip() for l in f if l.strip()]
        except Exception as e:
            print(f"Error reading pattern: {e}")
            return

        pattern = []
        for y, line in enumerate(lines):
            for x, c in enumerate(line):
                if c in {"O", "1"}:
                    pattern.append((x, y))

        if not pattern:
            print("No patern found")
            return

        offset_x = int(self.cam_x / self.cell_size)
        offset_y = int(self.cam_y / self.cell_size)
        center_x = (self.viewport().width() // (2 * self.cell_size)) + offset_x
        center_y = (self.viewport().height() // (2 * self.cell_size)) + offset_y

        for x, y in pattern:
            self.alive_cells.add((x + center_x, y + center_y))

        self.draw_grid()
        self.update_pop_label()

    def draw_grid(self):
        self.scene.clear()
        width = self.viewport().width()
        height = self.viewport().height()

        cols = width // self.cell_size + 2
        rows = height // self.cell_size + 2
        offset_x = self.cam_x % self.cell_size
        offset_y = self.cam_y % self.cell_size

        if self.show_grid:
            for x in range(0, cols):
                x_pos = x * self.cell_size - offset_x
                self.scene.addLine(x_pos, 0, x_pos, height, QColor(*colors["LIGHT_GREY"]))

            for y in range(0, rows):
                y_pos = y * self.cell_size - offset_y
                self.scene.addLine(0, y_pos, width, y_pos, QColor(*colors["LIGHT_GREY"]))

        for x, y in self.alive_cells:
            screen_x = (x * self.cell_size) - self.cam_x
            screen_y = (y * self.cell_size) - self.cam_y
            if 0 <= screen_x < width and 0 <= screen_y < height:
                rect = QGraphicsRectItem(screen_x, screen_y, self.cell_size, self.cell_size)
                rect.setBrush(QBrush(QColor(*colors["PURPLE"])))
                rect.setPen(QColor(*colors["BLACK"]))
                self.scene.addItem(rect)

    def checkNeighboor(self, x = None, y = None):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        count_CellAlive = 0
        if x == None or y == None:
            counts = Counter()
            for x, y in self.alive_cells:
                for dx, dy in directions:
                    counts[(x + dx, y + dy)] += 1

            new_alive = set()

            for cell, n in counts.items():
                # print(f"{cell} Voisins alive: {n}")
                if cell in self.alive_cells and n in self.nb_stay_alive:
                    new_alive.add(cell)
                elif cell not in self.alive_cells and n == self.nb_become_alive:
                    new_alive.add(cell)
            self.alive_cells = new_alive
        else:
            count_CellAlive = 0
            for i, j in directions:
                if (x + i, y + j) in self.alive_cells:
                    count_CellAlive += 1
            print(f"{x, y} Voisins alive: {count_CellAlive}") if count_CellAlive > 0 else None
            print("-"*20) if count_CellAlive > 0 else None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_A:
            self.key_press["a_press"] = True
            self.checkNeighboor()
        if event.key() == Qt.Key.Key_S:
            self.key_press["s_press"] = True

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_A:
            self.key_press["a_press"] = False
        if event.key() == Qt.Key.Key_S:
            self.key_press["s_press"] = False

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        mouse_pos = event.position()
        mouse_x = mouse_pos.x()
        mouse_y = mouse_pos.y()

        cell_x_before = (mouse_x + self.cam_x) / self.cell_size
        cell_y_before = (mouse_y + self.cam_y) / self.cell_size

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.cell_size = int(self.cell_size * zoom_factor)
        if self.cell_size < 4:
            self.cell_size = 4
        if self.cell_size > 300:
            self.cell_size = 300

        self.cam_x = cell_x_before * self.cell_size - mouse_x
        self.cam_y = cell_y_before * self.cell_size - mouse_y

        self.draw_grid()

    def resizeEvent(self, event):
        margin = 50
        self.speed_up_btn.move(self.width() - self.speed_up_btn.width() - margin, margin)
        self.speed_down_btn.move(self.width() - self.speed_down_btn.width() * 2 - margin - 5, margin)
        self.speed_label.move(self.width() - self.speed_label.width() - margin, self.speed_up_btn.height() + margin + 5)

        self.pop_label.move(5, self.height() - self.pop_label.height() - 15)

        self.draw_grid()
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        pos = event.position()
        cell_x = int((pos.x() + self.cam_x) // self.cell_size)
        cell_y = int((pos.y() + self.cam_y) // self.cell_size)
        cell = (cell_x, cell_y)

        if event.button() == Qt.MouseButton.LeftButton and self.key_press["s_press"]:
            self.checkNeighboor(cell_x, cell_y)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = pos
        if event.button() == Qt.MouseButton.RightButton:
            if cell in self.alive_cells:
                self.alive_cells.remove(cell)
            else:
                self.alive_cells.add(cell)
            self.draw_grid()
            # print(f"clic cellule : {cell}")

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is not None:
            delta = event.position() - self.last_mouse_pos
            self.cam_x -= delta.x()
            self.cam_y -= delta.y()
            self.last_mouse_pos = event.position()
            self.draw_grid()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = None

    def update_grid(self):
        self.update_speed_label()
        self.update_pop_label()
        self.checkNeighboor()
        self.draw_grid()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
    return 0

if __name__ == "__main__":
    main()
