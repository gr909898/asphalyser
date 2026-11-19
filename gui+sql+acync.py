from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys
import os
import traceback
import threading
from analyse import process_img
import sql

file_path = ""
openWindows = []

bg_res = None
bg_err = None

def photoImport():
    global file_path
    path, _ = QFileDialog.getOpenFileName(Window, "CHOOSE PHOTO", '', "Images (*.jpg *.jfif *.jpeg *.bmp *.png)")
    if path:
        file_path = path
        pixmap = QPixmap(file_path)


        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(0.5)
        pen = QPen(QColor(0, 255, 0))
        pen.setWidth(3)
        painter.setPen(pen)

        brush = QBrush(QColor(0, 255, 0))
        painter.setBrush(brush)

        brick_w = 80
        brick_h = 25

        x_pos = 20
        y_pos = pixmap.height() - brick_h - 20

        painter.drawRect(x_pos, y_pos, brick_w, brick_h)

        painter.end()
        
        photo.setPixmap(pixmap)
        text.setText("PHOTO LOADED")
        choose.setStyleSheet('background-color: green; color:white;')

def background_math():
    global bg_res, bg_err
    try:
        mask_bytes, plot_bytes, report_text, D_out, R2_out = process_img(file_path)  #!!!!!!!!!
        sql.save_result(file_path, D_out, R2_out)
        bg_res = (mask_bytes, plot_bytes, report_text)
        bg_err = None
    except Exception as e:
        bg_err = str(e)


def check():
    global bg_res, bg_err
    if bg_res is None and bg_err is None:
        return
    timer.stop()
    start.setEnabled(True)

    if bg_err:
        text.setText(str(bg_err))
        bg_err = None
        return

    mask_bytes, plot_bytes, report_text = bg_res
    text.setText(report_text)
    pm_mask = QPixmap()
    pm_mask.loadFromData(mask_bytes)
    w1 = QLabel()
    w1.setWindowTitle("Маска")
    w1.setPixmap(pm_mask)
    w1.setScaledContents(True)
    w1.resize(600, 450)
    w1.show()
        
    pm_plot = QPixmap()
    pm_plot.loadFromData(plot_bytes)
    w2 = QLabel()
    w2.setWindowTitle("График")
    w2.setPixmap(pm_plot)
    w2.setScaledContents(True)
    w2.resize(600, 450)
    w2.show()
        
    openWindows.extend([w1, w2])
    bg_res = None
    

    



def startwork():
    try:
        global bg_res, bg_err, timer
        
        if file_path and not photo.pixmap().isNull():
            text.setText('...')
            start.setEnabled(False)

            bg_res = None
            bg_err = None

            t = threading.Thread(target = background_math)
            t.start()

            timer = QTimer()
            timer.timeout.connect(check)
            timer.start(100)
            
        
            
        else:
            text.setText("NO PHOTO")
    except Exception:
        text.setText(traceback.format_exc())
        
def exit_click():
    Window.close()

app = QApplication(sys.argv)
Window = QWidget()
Window.resize(1020, 680)

#preview (добавить калибровочную маску)
photo = QLabel(Window)
photo.setStyleSheet('border: 1px solid gray;')
photo.setScaledContents(True)
photo.move(50, 150)
photo.resize(220, 180)

choose = QPushButton('CHOOSE PHOTO', Window)
choose.move(50, 100)
choose.resize(120, 30)

start = QPushButton('START', Window)
start.move(510, 500)
start.resize(200, 40)

buttonExit = QPushButton('╳', Window)
buttonExit.setStyleSheet('background-color: red; color:white; font-size: 20px;')
buttonExit.move(1, 1)
buttonExit.resize(40, 30)


text = QLabel('', Window)
text.setWordWrap(True)
text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
text.setStyleSheet('background-color: white; color:black; padding: 10px;')
text.move(300, 100)
text.resize(450, 360)

choose.clicked.connect(photoImport)
start.clicked.connect(startwork)
buttonExit.clicked.connect(exit_click)

sql.init_db()

Window.show()
sys.exit(app.exec())
