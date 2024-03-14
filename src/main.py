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
            event: dict[str, str] | None = None
            for line in lines:
                if event is None:
                    if line == "BEGIN:VEVENT": 
                        event = {}
                else: 
                    if line == "END:VEVENT": 
                        self.transform_dict_event(event)
                        event = None
                    else: 
                        [key, val] = line.split(':', 1)
                        event[key] = val


    
    def transform_dict_event(self, event: dict[str, str]): 
        titel = event.get("SUMMARY", "")
        beschreibung = event.get("DESCRIPTION", "")
        ort = event.get("LOCATION", "")

        date_s = event.get("DTSTART;VALUE=DATE") 
        time_s = ""

        if date_s is None: 
            s = event.get("DTSTART;TZID=Europe/Berlin")
            [date_s, time] = s.split("T", 1)
            time_s = format_time(time)
        date_s = format_date(date_s)

        date_e = event.get("DTEND;VALUE=DATE")
        time_e = ""

        if date_e is None: 
            s = event.get("DTEND;TZID=Europe/Berlin")
            [date_e, time] = s.split("T", 1)
            time_e = format_time(time)
        date_e = format_date(date_e)

        self.display_event([date_s, time_s, date_e, time_e, ort, titel, beschreibung])

    def display_event(self, event: List[str | date]):
        self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
        for column, el in enumerate(event):
            item = None
            if isinstance(el, str):
                item = QTableWidgetItem(el)
            else: 
                item = QTableWidgetItemDate(el)
            self.tableWidget.setItem(self.tableWidget.rowCount() -1 , column, item)


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
