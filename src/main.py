import sys
from datetime import date
from typing import List 
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem 

from ui_mainwindow import Ui_MainWindow


class QTableWidgetItemDate(QTableWidgetItem):   
    def __init__(self, d: date) -> None:
        self.date = d 
        super().__init__(str(d)) 

    def __lt__(self, other) -> bool:
        return self.date < other.date


def format_date(s: str) -> date:
    #s = "20201231"
    year = int(s[0:4])
    month = int(s[4:6])
    day = int(s[6:8])
    return date(year, month, day)

def format_time(s: str) -> str:
    #s = "245959"
    hours = s[0:2]
    minutes = s[2:4]
    return f"{hours}:{minutes}"

def parse_vevent(lines: List[str]) -> List[str | date]:
    #summary
    line = lines.pop(0)
    [_, value] = line.split(":", 1)
    title = value
    start = lines.pop(0)
    end = lines.pop(0)
    [key_start, value_start] = start.split(":", 1)
    [_, value_end] = end.split(":", 1)
    start_date =""
    start_time = ""
    end_date = ""
    end_time = ""
    if key_start.split("=",1)[1] == "DATE":
        start_date = format_date(value_start)
        end_date = format_date(value_end)
    else: 
        [date, time] = value_start.split("T", 1)
        start_date = format_date(date)
        start_time = format_time(time)    
        [date, time] = value_end.split("T", 1)
        end_date = format_date(date)
        end_time = format_time(time)
    #location or description 
    line = lines.pop(0)
    [key, value] = line.split(":", 1)
    ort = ""
    if key == "LOCATION": 
        ort = value
        line = lines.pop(0)
        [key, value] = line.split(":", 1)
    beschreibung = value
    return [
        start_date,
        start_time,
        end_date,
        end_time,
        ort,
        title,
        beschreibung 
    ]
    

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pb_open.clicked.connect(self.read_file)
        self.pb_fertig.setVisible(False)
        self.pb_new_event.clicked.connect(self.insert_row_4_event)
        self.pb_fertig.clicked.connect(self.finish_event)

    def read_file(self):
        self.tableWidget.setRowCount(0)
        (file_name, _) = QFileDialog.getOpenFileName(self)
        if file_name is None:
            print("no file selected")
            return

        with open(file_name, "r") as f:
            text = f.read() 
            lines = text.split("\n")
            line = lines.pop(0)
            while len(line) > 0: 
                while line != "BEGIN:VEVENT":
                    if len(lines) == 0: 
                        return
                    line = lines.pop(0)
                event = parse_vevent(lines)
                self.display_event(event) 
                line = lines.pop(0)


    def display_event(self, event: List[str | date]):
        t = self.tableWidget
        t.setRowCount(t.rowCount() + 1)
        for column, el in enumerate(event):
            if isinstance(el, str):
                t.setItem(t.rowCount() - 1, column, QTableWidgetItem(el))
            else: 
                t.setItem(t.rowCount() -1, column, QTableWidgetItemDate(el))


    def insert_row_4_event(self):
        self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
        self.pb_fertig.setVisible(True)
        self.pb_new_event.setVisible(False)


    def finish_event(self):
        t = self.tableWidget
        row = t.rowCount() -1 
        s = t.item(row, 0).text()
        #format dd.mm.yyyy
        day = int(s[0:2])
        month = int(s[3:5])
        year = int(s[6:10])
        item = QTableWidgetItemDate(date(year, month, day)) 
        t.setItem(row, 0, item)
        self.tableWidget.sortItems(0)
        self.pb_fertig.setVisible(False)
        self.pb_new_event.setVisible(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
