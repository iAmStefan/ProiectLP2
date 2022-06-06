from datetime import datetime
from tkinter.ttk import *
import pandas as pd
import requests
import os
import csv
from tkinter import *
from unidecode import unidecode
from PIL import Image, ImageTk
from tkcalendar import *
import plotly.express as px

url = 'https://data.primariatm.ro/dataset/56ac723e-62af-443a-8811-554db730a961/resource/8fb1e450-7cc2-4a6b-bee0-1f88f206c56c/download/siguran-i-ordine-public.csv'

window = Tk()
window.title('Proiect LP')
window.resizable(False, False)
window.geometry("1070x500")
indicatori = list()
indexes = list()

def showCalendar(event):
    start_date.place(x=150, y=250)
    end_date.place(x=150, y=290)
    start_calendar.place(x=25, y=248)
    end_calendar.place(x=25, y=288)
    setare_date.place(x=25, y=325)

meniu_indicatori = Combobox(window, width=40, font=("Arial", 12))
meniu_indicatori.set("Selectați indicatorul dorit")
meniu_indicatori.bind('<<ComboboxSelected>>', showCalendar)
meniu_indicatori.place(x=25, y=170)

info = Label(text="Indicatori:", font=("Arial", 12)).place(x=25, y=130)

start_date = DateEntry(window, selectmode="day", year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
end_date = DateEntry(window, selectmode="day", year=datetime.today().year, month=datetime.today().month, day=datetime.today().day)
start_calendar = Label(text="Data de început:", font=("Arial", 12))
end_calendar = Label(text="Data de final:", font=("Arial", 12))
year_range = Label(text="", font=("Arial", 12))

def descarcare(event):
    if not os.path.exists('out.csv'):
        response = requests.get(url)
        with open('out.csv', 'wb') as file:
            for line in response:
                file.write(line)
            download_status['text'] = "Descărcarea s-a terminat!"
            file.close()
            with open('out.csv', 'r') as f_in:
                csv_reader = csv.reader(f_in, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        line_count += 1
                    else:
                        row[0] = unidecode(row[0])
                        row[0] = row[0].replace("A(r)", "î")
                        row[0] = row[0].replace("Af", "ă")
                        row[0] = row[0].replace("E(tm)", "ș")
                        row[0] = row[0].replace("E>", "ț")
                        row[0] = row[0].replace("AC/", "â")
                        indicatori.append(row[0])
                        line_count += 1
                        meniu_indicatori["values"] = indicatori
    else:
        download_status['text'] = "Fișierul există deja"

year_start = ""
year_end = ""

def find_year_data(year_start, year_end):
    with open("out.csv") as f_in:
        csv_reader = csv.reader(f_in, delimiter=",")
        line_count = 0
        for line in csv_reader:
            if line_count == 0:
                try:
                    if (year_start and year_end) or (year_start or year_end) in line:
                        index_start = line.index(year_start)
                        index_end = line.index(year_end)
                        indexes.append(index_start)
                        indexes.append(index_end)
                    line_count += 1
                except ValueError:
                    year_range["text"] = "Anii introduși nu se regăsesc în fișier."
                    year_range.place(x=25, y=325)
                    setare_date.place(x=25, y=360)
            else:
                line_count += 1

def get_date(event):
    year_range["text"] = ""
    year_range.pack_forget()
    setare_date.place(x=25, y=335)
    data_calendar1 = start_date.get_date()
    year_start = data_calendar1.strftime('%Y')
    data_calendar2 = end_date.get_date()
    year_end = data_calendar2.strftime('%Y')
    if year_range["text"] == "":
        if year_end < year_start:
            year_range["text"] = "Anul de început trebuie să fie mai mic decât cel de sfârșit."
            year_range.place(x=25, y=325)
            setare_date.place(x=25, y=360)
        find_year_data(year_start, year_end)
        if year_range["text"] == "":
            export_data.place(x=150, y=335)

setare_date = Button(window, text="Setare date", font=("Tahoma", 12), width=11, height=1)
setare_date.bind('<Button-1>', get_date)

if os.path.exists('out.csv'):
    with open('out.csv', 'r') as f_in:
        csv_reader = csv.reader(f_in, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                row[0] = unidecode(row[0])
                row[0] = row[0].replace("A(r)", "î")
                row[0] = row[0].replace("Af", "ă")
                row[0] = row[0].replace("E(tm)", "ș")
                row[0] = row[0].replace("E>", "ț")
                row[0] = row[0].replace("AC/", "â")
                indicatori.append(row[0])
                line_count += 1
                meniu_indicatori["values"] = indicatori

download = Button(window, text="Descărcare", font=('Tahoma', 12), width=11, height=1)
download.bind('<Button-1>', descarcare)
download.place(x=25, y=25)

download_status = Label(text="", font=("Arial", 12))
download_status.place(x=25, y=65)

def export(event):
    data = pd.read_csv("out.csv")
    data = data[data['SIGURANȚĂ ȘI ORDINE PUBLICĂ'] == meniu_indicatori.get()]
    data = data.iloc[:, indexes[1]:indexes[0]+1]
    data = data.transpose()
    data = data.reindex(index=data.index[::-1])
    fig = px.bar(data, labels={'index': 'Ani', 'value': meniu_indicatori.get()}, title="Siguranță și ordine publică")
    fig.layout.update(showlegend=False)
    fig.write_image('chart.jpeg')
    img = (Image.open("chart.jpeg"))
    resized_image = img.resize((610, 442))
    new_image = ImageTk.PhotoImage(resized_image)
    poza = Label(window, image=new_image)
    poza.image = new_image
    poza.place(x=430, y=25)

export_data = Button(window, text="Afișare grafic", font=('Tahoma', 12), width=11, height=1)
export_data.bind('<Button-1>', export)

window.mainloop()