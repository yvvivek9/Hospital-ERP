from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter.filedialog import askdirectory
from glob import glob
from os.path import expanduser
from docxtpl import DocxTemplate
from win32com import client
import threading
import pandas as pd
import sqlite3
import os
import datetime
import time
import json

#python -m PyInstaller --noconsole --onedir --windowed main.py

table_row_count = 1
treat_row_count = 1
treatment = []
cost = 0
due = 0



def updateBillNoJSON(number1, number2):
    dictionary = {
        "billno": number1,
        "pid": number2
    }
    with open("data.json", "w") as outfile:
        json.dump(dictionary, outfile)


def popup(text):
    pop = Tk()
    pop.overrideredirect(True)
    pop.geometry("300x100")
    pop.eval("tk::PlaceWindow . center")
    popFrame = Frame(pop, bd=5, relief=SOLID)
    popFrame.place(x=0, y=0, width=300, height=100)
    error = Label(popFrame, text=text, font=("times new roman", 10))
    error.place(x=50, y=10, width=200, height=20)
    ok = Button(popFrame, text="OK", font=("arial", 10), command=pop.destroy)
    ok.place(x=100, y=50, width=100, height=20)

def exportCSV():
    def export(duration, window):
        conn = sqlite3.connect("sql.db")
        cursor = conn.cursor()
        if(duration == "all-time"):
            clients = pd.read_sql("SELECT * FROM PATIENTS", conn)
            clients.loc['Total'] = clients[['Cost', 'Due']].sum(axis=0)
            dir = askdirectory(title='Select Folder')
            path = os.path.join(dir, "billing-data.xlsx") 
            clients.to_excel(path, index=False)
        else:
            current_time = datetime.datetime.now()
            date = str(current_time.day) + "/" + str(current_time.month) + "/" + str(current_time.year)
            query = """SELECT * FROM PATIENTS WHERE Date='{date}'"""
            query2 = query.format(date=date)
            clients = pd.read_sql(query2, conn)
            clients.loc['Total'] = clients[['Cost', 'Due']].sum(axis=0)
            dir = askdirectory(title='Select Folder')
            path = os.path.join(dir, "billing-data.xlsx") 
            clients.to_excel(path, index=False)
        conn.close()
        window.destroy()
    pop = Tk()
    pop.geometry("200x100")
    pop.eval("tk::PlaceWindow . center")
    popFrame = Frame(pop)
    popFrame.place(x=0, y=0, width=200, height=100)
    error = Button(popFrame, text="Today", font=("arial", 10, "bold"), command=lambda : export("today", pop))
    error.place(x=50, y=15, width=100, height=20)
    ok = Button(popFrame, text="All Time", font=("arial", 10, "bold"), command=lambda : export("all-time", pop))
    ok.place(x=50, y=55, width=100, height=20)
    pop.mainloop()


def printBill(billNo):
    def searchByBill(billNo):
        try:
            db = sqlite3.connect("sql.db")
            cursor = db.cursor()
            data = cursor.execute("SELECT * FROM PATIENTS WHERE Bill_No=?", (billNo,))
            for row in data:
                return row
        except sqlite3.Error as error:
            popup(error)
        finally:
            db.close()

    patient = searchByBill(billNo)
    treat = patient[10]
    treatArray = []
    i = 1
    for j in treat.split(" | "):
        if(j != ""):
            name, quantity, tCost = j.split(":")
            treatArray.append([str(i), name, quantity, tCost, str(int(quantity)*int(tCost))])
            i += 1
    doc = DocxTemplate("bill_tmpl.docx")
    content = {
        "billNo": patient[0],
        "pid": patient[1],
        "date": patient[2],
        "name": patient[4],
        "age": patient[5],
        "gender": patient[6],
        "consultant": patient[7],
        "referred": patient[8],
        "Treatments": treatArray,
        "amount": patient[11],
        "due": patient[12]
    }
    doc.render(content)
    doc.save("generated_doc.docx")
    word = client.Dispatch("Word.Application")
    word.Documents.Open(os.path.join(os.getcwd(), "generated_doc.docx"))
    word.ActiveDocument.PrintOut()
    time.sleep(2)
    word.ActiveDocument.Close()
    word.Quit()

def addDue():
    window = Tk()
    window.overrideredirect(True)
    window.geometry("300x130")
    window.eval("tk::PlaceWindow . center")
    windowFrame = Frame(window, bd=5, relief=SOLID)
    windowFrame.place(x=0, y=0, width=300, height=130)
    lblDue = Label(windowFrame, text="Enter the due amount:", font=("times new roman", 15))
    lblDue.place(x=30, y=10, width=200, height=20)
    entDue = Entry(windowFrame, 
            font=("arial", 10, "bold"),
            bd=2,
            bg="white",
            width=30,
            relief=RIDGE)
    entDue.insert(0, due)
    entDue.place(x=30, y=40)
    cancelBtn = Button(windowFrame,
        font=("arial", 10, "bold"),
        text="Cancel",
        bg="red",
        fg="white",
        command=window.destroy
    )
    cancelBtn.place(x=40, y=80, width=100, height=20)
    def updateDue():
        global due
        due = entDue.get()
        window.destroy()
    updateBtn = Button(windowFrame,
        font=("arial", 10, "bold"),
        text="Add Due",
        bg="green",
        fg="white",
        command=updateDue
    )
    updateBtn.place(x=150, y=80, width=100, height=20)
    window.mainloop()

class opd:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice generation")
        self.root.geometry("1500x800")
        self.root.resizable(False, False)

        lbltitle = Label(
            self.root,
            text="Sree Venkateshwara Speciality Hospital",
            bd=15,
            relief=RIDGE,
            bg="white",
            fg="black",
            font=("times new roman", 20, "bold"),
            padx=2,
            pady=4,
        )
        lbltitle.pack(side=TOP, fill=X)

        # img1=Image.open(r"th.jpeg")
        # img1=img1.resize((38,38))
        # self.photoimg1=ImageTk.PhotoImage(img1)
        # b1=Button(self.root,image=self.photoimg1,borderwidth=0)
        # b1.place(x=450,y=16)

        # img2=Image.open(r"th.jpeg")
        # img2=img2.resize((38,38))
        # self.photoimg2=ImageTk.PhotoImage(img2)
        # b1=Button(self.root,image=self.photoimg2,borderwidth=0)
        # b1.place(x=1010,y=16)

        # ==================================DATAFRAME====================================================
        self.DataFrame = Frame(self.root, bd=5, relief=RIDGE, padx=2)
        self.DataFrame.place(x=0, y=69, width=1500, height=400)

        DataFrameLeft = LabelFrame(
            self.DataFrame,
            bd=5,
            relief=RIDGE,
            padx=20,
            text="Patient Info",
            fg="black",
            font=("arial", 10, "bold"),
        )
        DataFrameLeft.place(x=0, y=0, width=735, height=350)

        self.__initRightFrame()

        # ================================BUTTONFRAME====================================================

        ButtonFrame = Frame(self.root, bd=15, relief=RIDGE, padx=20)
        ButtonFrame.place(x=0, y=430, width=1500, height=65)

        self.__initTableFrame()
        # ================================Main Button====================================================

        # btnAddData=Button(ButtonFrame,text="Update",fg="white",width=14,font=("arial",10,'bold'),bg='LightGoldenrod4')
        # btnAddData.grid(row=0,column=1)

        # btnAddData=Button(ButtonFrame,text="Delete",fg="white",width=14,font=("arial",10,'bold'),bg='red')
        # btnAddData.grid(row=0,column=2)

        self.search_combo0 = ttk.Combobox(
            ButtonFrame, width=12, font=("arial", 10, "bold"), state="readonly"
        )
        self.search_combo0["values"] = ("Bill No", "Name")
        self.search_combo0.grid(row=0, column=1)
        self.search_combo0.current(0)

        self.textSearch = Entry(
            ButtonFrame, bd=3, relief=RIDGE, width=25, font=("arial", 10, "bold")
        )
        self.textSearch.grid(row=0, column=2)

        btnSearchData = Button(
            ButtonFrame,
            text="Search",
            fg="white",
            width=14,
            font=("arial", 10, "bold"),
            bg="green",
            command=self.__search_window,
        )
        btnSearchData.grid(row=0, column=3)

        downloadCSV = Button(
            ButtonFrame,
            text="Download .xlsx",
            fg="white",
            width=14,
            font=("arial", 10, "bold"),
            bg="green",
            command=exportCSV,
        )
        downloadCSV.grid(row=0, column=4, padx=850, pady=5)

        # ===================================Patient Info Labels===============================================

        self.lblBillNo = Label(
            DataFrameLeft, font=("arial", 10, "bold"), text="Bill No.", padx=2, pady=9
        )
        self.lblBillNo.grid(row=0, column=0)
        self.txtBillNo = Entry(
            DataFrameLeft,
            font=("arial", 10, "bold"),
            bd=2,
            bg="white",
            width=29,
            relief=RIDGE,
        )
        self.txtBillNo.grid(row=0, column=1)

        btnGenBillNo = Button(
            DataFrameLeft,
            text="Generate Bill No",
            command=self.__generateBillNo,
            fg="white",
            width=14,
            font=("arial", 10, "bold"),
            bg="green",
        )
        btnGenBillNo.grid(row=0, column=2, padx=10)

        lblpid = Label(
            DataFrameLeft, font=("arial", 10, "bold"), text="Patient ID", padx=2, pady=6
        )
        lblpid.grid(row=1, column=0)
        self.txtpid = Entry(
            DataFrameLeft,
            font=("arial", 10, "bold"),
            bd=2,
            bg="white",
            width=29,
            relief=RIDGE,
        )
        self.txtpid.grid(row=1, column=1)

        lblpname = Label(
            DataFrameLeft, font=("arial", 10, "bold"), text="Name", padx=2, pady=6
        )
        lblpname.grid(row=3, column=0)
        self.txtpname = Entry(
            DataFrameLeft,
            font=("arial", 10, "bold"),
            bd=2,
            bg="white",
            width=29,
            relief=RIDGE,
        )
        self.txtpname.grid(row=3, column=1)

        lblPage = Label(
            DataFrameLeft, font=("arial", 10, "bold"), text="Age", padx=2, pady=6
        )
        lblPage.grid(row=5, column=0)
        self.txtPage = Entry(
            DataFrameLeft,
            font=("arial", 10, "bold"),
            bd=2,
            bg="white",
            width=29,
            relief=RIDGE,
        )
        self.txtPage.grid(row=5, column=1)

        lblPsex = Label(
            DataFrameLeft, font=("arial", 10, "bold"), text="Gender", padx=2, pady=6
        )
        lblPsex.grid(row=7, column=0)
        self.search_combo1 = ttk.Combobox(
            DataFrameLeft, width=12, font=("arial", 10, "bold"), state="readonly"
        )
        self.search_combo1["values"] = ("M", "F")
        self.search_combo1.grid(row=7, column=1)
        self.search_combo1.current(0)

        lblCons = Label(
            DataFrameLeft,
            font=("arial", 10, "bold"),
            text="Consultant ",
            padx=2,
            pady=6,
        )
        lblCons.grid(row=8, column=0)
        self.search_combo2 = ttk.Combobox(
            DataFrameLeft, width=25, font=("arial", 10, "bold"), state="normal"
        )
        self.search_combo2["values"] = (
            "Dr.H.N.VENKATESH [GENERAL PHYSICIAN]",
            "Dr.SYED [PHYSIOTHERAPY]",
            " ",
        )
        self.search_combo2.grid(row=8, column=1)
        self.search_combo2.current(0)

        lblrefby = Label(
            DataFrameLeft,
            font=("arial", 10, "bold"),
            text="Reffered by ",
            padx=2,
            pady=6,
        )
        lblrefby.grid(row=9, column=0)
        self.search_combo3 = ttk.Combobox(
            DataFrameLeft, width=25, font=("arial", 10, "bold"), state="normal"
        )
        self.search_combo3["values"] = (
            "Dr.H.N.VENKATESH [GENERAL PHYSICIAN]",
            "Dr.SYED [PHYSIOTHERAPY]",
            " ",
        )
        self.search_combo3.grid(row=9, column=1)
        self.search_combo3.current(0)

        lblpay = Label(
            DataFrameLeft, font=("arial", 10, "bold"), text="Payment ", padx=2, pady=6
        )
        lblpay.grid(row=10, column=0)
        self.search_combo4 = ttk.Combobox(
            DataFrameLeft, width=25, font=("arial", 10, "bold"), state="readonly"
        )
        self.search_combo4["values"] = ("Cash", "Paytm")
        self.search_combo4.grid(row=10, column=1)
        self.search_combo4.current(0)

        temp = Label(DataFrameLeft).grid(row=11, column=1)

        btnAddData = Button(
            DataFrameLeft,
            text="Patient Add",
            command=self.__addPatient,
            fg="white",
            width=14,
            font=("arial", 10, "bold"),
            bg="green",
        )
        btnAddData.grid(row=12, column=0)

        btnAddData = Button(
            DataFrameLeft,
            text="Generate Invoice",
            fg="white",
            width=14,
            font=("arial", 10, "bold"),
            bg="green",
            command=lambda : printBill(self.txtBillNo.get()),
        )
        btnAddData.grid(row=12, column=1)

        btnAddData = Button(
            DataFrameLeft,
            text="Reset",
            fg="white",
            width=14,
            font=("arial", 10, "bold"),
            bg="blue",
            command=self.__reset,
        )
        btnAddData.grid(row=12, column=2)

        self.lblCost = Label(
            DataFrameLeft,
            font=("arial", 15, "bold"),
            text=f"Total: {cost} INR",
            padx=30,
        )
        self.lblCost.grid(row=11, column=3)

        btnAddDue = Button(
            DataFrameLeft,
            text="Add Due",
            fg="white",
            width=14,
            font=("arial", 10, "bold"),
            bg="blue",
            command=addDue,
        )
        btnAddDue.grid(row=12, column=3)

        ############################ CHECKING DATABASE ###########################################

        if not os.path.isfile("sql.db"):
            self.__addTableSql()

    def __reset(self):
        global cost, treatment, treat_row_count, due
        allEntries = [self.txtBillNo, self.txtpid, self.txtpname, self.txtPage]
        for i in allEntries:
            i.delete(0, END)
        allCombo = [
            self.search_combo1,
            self.search_combo2,
            self.search_combo3,
            self.search_combo4,
        ]
        for i in allCombo:
            i.current(0)
        self.DataFrameRight.destroy()
        self.__initRightFrame()
        cost = 0
        treat_row_count = 1
        due = 0
        self.lblCost.config(text=f"Cost: {cost}")
        treatment.clear()

    def __initRightFrame(self):
        self.DataFrameRight = LabelFrame(
            self.DataFrame,
            bd=5,
            relief=RIDGE,
            padx=20,
            text="Treatment",
            fg="black",
            font=("arial", 10, "bold"),
        )
        self.DataFrameRight.place(x=745, y=0, width=735, height=350)
        addTreatLabel = Button(
            self.DataFrameRight,
            font=("arial", 10, "bold"),
            text="Add Treatment",
            bg="blue",
            fg="white",
            command=self.__treatment_window,
        )
        addTreatLabel.grid(row=0, column=0, pady=10)

    def __initTableFrame(self):
        self.TableFrame = Frame(self.root, bd=15, relief=RIDGE)
        self.TableFrame.place(x=0, y=505, width=1500, height=535)

        col1 = Label(
            self.TableFrame,
            font=("arial", 10, "bold"),
            text="Bill No",
            borderwidth=2,
            relief="solid",
            width=10,
            padx=2,
            pady=9,
        )
        col1.grid(row=0, column=0, padx=(40, 0))
        col2 = Label(
            self.TableFrame,
            font=("arial", 10, "bold"),
            text="ID",
            borderwidth=2,
            relief="solid",
            width=10,
            padx=2,
            pady=9,
        )
        col2.grid(row=0, column=1)
        col3 = Label(
            self.TableFrame,
            font=("arial", 10, "bold"),
            text="Name",
            borderwidth=2,
            relief="solid",
            width=20,
            padx=2,
            pady=9,
        )
        col3.grid(row=0, column=2)
        col4 = Label(
            self.TableFrame,
            font=("arial", 10, "bold"),
            text="Age",
            borderwidth=2,
            relief="solid",
            width=5,
            padx=2,
            pady=9,
        )
        col4.grid(row=0, column=3)
        col5 = Label(
            self.TableFrame,
            font=("arial", 10, "bold"),
            text="Gender",
            borderwidth=2,
            relief="solid",
            width=10,
            padx=2,
            pady=9,
        )
        col5.grid(row=0, column=4)
        col6 = Label(
            self.TableFrame,
            font=("arial", 10, "bold"),
            text="Consultant",
            borderwidth=2,
            relief="solid",
            width=50,
            padx=2,
            pady=9,
        )
        col6.grid(row=0, column=5)
        col7 = Label(
            self.TableFrame,
            font=("arial", 10, "bold"),
            text="Referrer",
            borderwidth=2,
            relief="solid",
            width=50,
            padx=2,
            pady=9,
        )
        col7.grid(row=0, column=6)
        col8 = Label(
            self.TableFrame,
            font=("arial", 10, "bold"),
            text="Payment",
            borderwidth=2,
            relief="solid",
            width=10,
            padx=2,
            pady=9,
        )
        col8.grid(row=0, column=7)

    def __search_window(self):
        def delByBillNo(billno, window):
            try:
                db = sqlite3.connect("sql.db")
                cursor = db.cursor()
                delete = """DELETE FROM PATIENTS WHERE Bill_No=?"""
                cursor.execute(delete, (billno,))
                db.commit()
                window.destroy()
            except sqlite3.Error as error:
                popup("Error occured: " + str(error))
            finally:
                db.close()

        def updateByBillNo(billno, window, data):
            delByBillNo(billno, window)
            try:
                db = sqlite3.connect("sql.db")
                cursor = db.cursor()
                query = """INSERT INTO PATIENTS VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                cursor.execute(
                    query,
                    (
                        data[0],
                        data[1],
                        data[2],
                        data[3],
                        data[4],
                        data[5],
                        data[6],
                        data[7],
                        data[8],
                        data[9],
                        data[10],
                        data[11],
                        data[12],
                    )
                )
                db.commit()
            except sqlite3.Error as error:
                print(error)
            finally:
                db.close()

        def printByBillNo(billno, window):
            window.destroy()
            printBill(billno)

        def openWindow(data):
            window = Tk()
            window.geometry("500x750")
            window.title("Patient Search")

            lblBill = Label(
                window, font=("arial", 10, "bold"), text="Bill No:", width=10
            )
            lblBill.grid(row=0, column=0, padx=30, pady=20)
            entBill = Entry(
                window, font=("arial", 10, "bold"), width=40, bd=1, relief=SOLID
            )
            entBill.insert(0, data[0])
            entBill.grid(row=0, column=1, pady=10)

            lblPid = Label(
                window, font=("arial", 10, "bold"), text="Patient ID:", width=10
            )
            lblPid.grid(row=1, column=0, padx=30, pady=5)
            entPid = Entry(
                window, font=("arial", 10, "bold"), width=40, bd=1, relief=SOLID
            )
            entPid.insert(0, data[1])
            entPid.grid(row=1, column=1, pady=10)

            lblDate = Label(window, font=("arial", 10, "bold"), text="Date:", width=10)
            lblDate.grid(row=2, column=0, padx=30, pady=5)
            entDate = Entry(
                window, font=("arial", 10, "bold"), width=40, bd=1, relief=SOLID
            )
            entDate.insert(0, data[2])
            entDate.grid(row=2, column=1, pady=10)

            lblTime = Label(window, font=("arial", 10, "bold"), text="Time:", width=10)
            lblTime.grid(row=3, column=0, padx=30, pady=5)
            entTime = Entry(
                window, font=("arial", 10, "bold"), width=40, bd=1, relief=SOLID
            )
            entTime.insert(0, data[3])
            entTime.grid(row=3, column=1, pady=10)

            lblName = Label(window, font=("arial", 10, "bold"), text="Name:", width=10)
            lblName.grid(row=4, column=0, padx=30, pady=5)
            entName = Entry(
                window, font=("arial", 10, "bold"), width=40, bd=1, relief=SOLID
            )
            entName.insert(0, data[4])
            entName.grid(row=4, column=1, pady=10)

            lblAge = Label(window, font=("arial", 10, "bold"), text="Age:", width=10)
            lblAge.grid(row=5, column=0, padx=30, pady=5)
            entAge = Entry(
                window, font=("arial", 10, "bold"), width=40, bd=1, relief=SOLID
            )
            entAge.insert(0, data[5])
            entAge.grid(row=5, column=1, pady=10)

            lblGender = Label(
                window, font=("arial", 10, "bold"), text="Gender:", width=10
            )
            lblGender.grid(row=6, column=0, padx=30, pady=5)
            entGender = Entry(
                window, font=("arial", 10, "bold"), width=40, bd=1, relief=SOLID
            )
            entGender.insert(0, data[6])
            entGender.grid(row=6, column=1, pady=10)

            lblConsultant = Label(
                window, font=("arial", 10, "bold"), text="Consultant:", width=10
            )
            lblConsultant.grid(row=7, column=0, padx=30, pady=5)
            entConsultant = Text(
                window,
                font=("arial", 10, "bold"),
                width=40,
                height=2,
                bd=1,
                relief=SOLID,
            )
            entConsultant.insert("1.0", data[7])
            entConsultant.grid(row=7, column=1, pady=10)

            lblReff = Label(
                window, font=("arial", 10, "bold"), text="Referred By:", width=10
            )
            lblReff.grid(row=8, column=0, padx=30, pady=5)
            entReff = Text(
                window,
                font=("arial", 10, "bold"),
                width=40,
                height=2,
                bd=1,
                relief=SOLID,
            )
            entReff.insert("1.0", data[8])
            entReff.grid(row=8, column=1, pady=10)

            lblPayment = Label(
                window, font=("arial", 10, "bold"), text="Payment:", width=10
            )
            lblPayment.grid(row=9, column=0, padx=30, pady=5)
            entPayment = Entry(
                window, font=("arial", 10, "bold"), width=40, bd=1, relief=SOLID
            )
            entPayment.insert(0, data[9])
            entPayment.grid(row=9, column=1, pady=10)

            lblServices = Label(
                window, font=("arial", 10, "bold"), text="Services:", width=10
            )
            lblServices.grid(row=10, column=0, padx=30, pady=5)
            entServices = Text(
                window,
                font=("arial", 10, "bold"),
                width=40,
                height=5,
                bd=1,
                relief=SOLID,
            )
            entServices.insert("1.0", data[10])
            entServices.grid(row=10, column=1, pady=10)

            lblCost = Label(window, font=("arial", 10, "bold"), text="Cost:", width=10)
            lblCost.grid(row=11, column=0, padx=30, pady=5)
            entCost = Entry(
                window, font=("arial", 10, "bold"), width=40, bd=1, relief=SOLID
            )
            entCost.insert(0, data[11])
            entCost.grid(row=11, column=1, pady=10)

            lblDue = Label(window, font=("arial", 10, "bold"), text="Due:", width=10)
            lblDue.grid(row=12, column=0, padx=30, pady=5)
            entDue = Entry(
                window, font=("arial", 10, "bold"), width=40, bd=1, relief=SOLID
            )
            entDue.insert(0, data[12])
            entDue.grid(row=12, column=1, pady=10)

            btndel = Button(
                window,
                font=("arial", 10, "bold"),
                text="Delete",
                bg="red",
                fg="white",
                command=lambda: delByBillNo(entBill.get(), window),
            )
            btndel.grid(row=13, column=0, pady=10)
            btnupdate = Button(
                window,
                font=("arial", 10, "bold"),
                text="Update",
                bg="blue",
                fg="white",
                command=lambda: updateByBillNo(
                    entBill.get(),
                    window,
                    [
                        entBill.get(),
                        entPid.get(),
                        entDate.get(),
                        entTime.get(),
                        entName.get(),
                        entAge.get(),
                        entGender.get(),
                        entConsultant.get("1.0", "end-1c"),
                        entReff.get("1.0", "end-1c"),
                        entPayment.get(),
                        entServices.get("1.0", "end-1c"),
                        entCost.get(),
                        entDue.get(),
                    ],
                ),
            )
            btnupdate.grid(row=13, column=1, pady=10)
            btninvoice = Button(
                window,
                font=("arial", 10, "bold"),
                text="Generate Invoice",
                bg="green",
                fg="white",
                command=lambda : printByBillNo(data[0], window)
            )
            btninvoice.grid(row=14, column=1, pady=5)

            window.mainloop()

        def searchByBill(billno):
            try:
                db = sqlite3.connect("sql.db")
                cursor = db.cursor()
                text = """SELECT * FROM PATIENTS WHERE Bill_No=?"""
                data = cursor.execute(text, (billno,))
                for row in data:
                    openWindow(row)
            except sqlite3.Error as error:
                popup(error)
            finally:
                db.close()

        def searchByName(name):
            try:
                db = sqlite3.connect("sql.db")
                cursor = db.cursor()
                text = """SELECT * FROM PATIENTS WHERE Name=?"""
                data = cursor.execute(text, (name,))
                for row in data:
                    threading.Thread(target=openWindow, args=[row]).start()
            except sqlite3.Error as error:
                popup(error)
            finally:
                db.close()

        if self.textSearch.get() != "":
            if self.search_combo0.get() == "Bill No":
                searchByBill(self.textSearch.get())
            elif self.search_combo0.get() == "Name":
                searchByName(self.textSearch.get())
        else:
            popup("Check your inputs")

    def __treatment_window(self):
        treat = Tk()
        treat.overrideredirect(True)
        treat.geometry("380x250")
        treat.eval("tk::PlaceWindow . center")
        treatFrame = Frame(treat, bd=5, relief=SOLID)
        treatFrame.place(x=0, y=0, width=380, height=250)
        lblDetail = Label(
            treatFrame, font=("arial", 10, "bold"), text="Treatment \n Details:"
        )
        lblDetail.place(x=10, y=10, width=70, height=50)
        treatDetails = Text(treatFrame, width=35, height=5, font=("arial", 10))
        treatDetails.place(x=100, y=10)
        lblQuantity = Label(treatFrame, font=("arial", 10, "bold"), text="Quantity:")
        lblQuantity.place(x=10, y=110)
        entryQuantity = Entry(treatFrame, width=20, font=("arial", 10))
        entryQuantity.place(x=100, y=110)
        lblCost = Label(treatFrame, font=("arial", 10, "bold"), text="Cost:")
        lblCost.place(x=15, y=150)
        entryCost = Entry(treatFrame, width=20, font=("arial", 10))
        entryCost.place(x=100, y=150)

        def fwd_treatment():
            self.__addTreatment(
                treatDetails.get("1.0", "end-1c"), entryQuantity.get(), entryCost.get()
            )
            treat.destroy()

        cancel = Button(
            treatFrame, font=("arial", 10, "bold"), text="Cancel", command=treat.destroy
        )
        cancel.place(x=100, y=200)
        submit = Button(
            treatFrame, font=("arial", 10, "bold"), text="Add", command=fwd_treatment
        )
        submit.place(x=180, y=200)
        treat.mainloop()

    def __delTreatment(self, name, tempCost, label, button):
        global treatment, cost
        treatment.remove(name)
        label.destroy()
        button.destroy()
        cost -= tempCost
        self.lblCost.config(text=f"Cost: {cost}")

    def __addTreatment(self, name, quantity, addCost):
        global cost, treat_row_count, treatment
        try:
            tempCost = int(addCost) * int(quantity)
            cost += tempCost
            treat = name + ":" + quantity + ":" + addCost
            treatment.append(treat)
            self.lblCost.config(text=f"Cost: {cost}")
            temp_lbl = Label(
                self.DataFrameRight,
                font=("arial", 10, "bold"),
                text=f"{treat_row_count}) {name}, Quantity: {quantity}, Cost: {tempCost}",
                anchor="w",
                width=60,
                bd=1,
                relief=SOLID,
                padx=5,
                pady=5,
            )
            temp_lbl.grid(row=treat_row_count, column=0)
            temp_btn = Button(
                self.DataFrameRight,
                font=("arial", 10, "bold"),
                text="Delete",
                command=lambda: self.__delTreatment(treat, tempCost, temp_lbl, temp_btn),
            )
            temp_btn.grid(row=treat_row_count, column=1)
            treat_row_count += 1
        except:
            popup("Check your inputs")

    def __generateBillNo(self):
        f = open('data.json')
        data = json.load(f)
        oldBillNo = data["billno"]
        oldPidNo = data["pid"]
        f.close()
        newBillNo = str(int(oldBillNo) + 1)
        newBillStr = newBillNo + "/23-24"
        newPidNo = str(int(oldPidNo) + 1)
        newPidStr = "SVH00" + newPidNo
        self.txtBillNo.delete(0, END)
        self.txtBillNo.insert(0, newBillStr)
        self.txtpid.delete(0, END)
        self.txtpid.insert(0, newPidStr)
        updateBillNoJSON(newBillNo, newPidNo)

    def __addPatient(self):
        global cost, treatment, due
        if (
            self.txtBillNo.get() != ""
            and self.txtpid.get() != ""
            and self.txtpname.get() != ""
            and self.txtPage.get() != ""
            and self.search_combo1.get() != ""
            and self.search_combo2.get() != ""
            and self.search_combo3.get() != ""
            and self.search_combo4.get() != ""
        ):
            current_time = datetime.datetime.now()
            strTreat = ""
            for i in treatment:
                strTreat += i
                strTreat += " | "
            try:
                db = sqlite3.connect("sql.db")
                cursor = db.cursor()
                insert = """INSERT INTO PATIENTS VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                cursor.execute(
                    insert,
                    (
                        self.txtBillNo.get(),
                        self.txtpid.get(),
                        str(current_time.day)
                        + "/"
                        + str(current_time.month)
                        + "/"
                        + str(current_time.year),
                        str(current_time.hour)
                        + ":"
                        + str(current_time.minute)
                        + ":"
                        + str(current_time.second),
                        self.txtpname.get(),
                        self.txtPage.get(),
                        self.search_combo1.get(),
                        self.search_combo2.get(),
                        self.search_combo3.get(),
                        self.search_combo4.get(),
                        strTreat,
                        cost,
                        due,
                    ),
                )
                db.commit()
                self.__addToTable(
                    self.txtBillNo.get(),
                    self.txtpid.get(),
                    self.txtpname.get(),
                    self.txtPage.get(),
                    self.search_combo1.get(),
                    self.search_combo2.get(),
                    self.search_combo3.get(),
                    self.search_combo4.get(),
                    strTreat,
                    cost,
                    due,
                )
            except sqlite3.Error as error:
                popup(error)
            finally:
                db.close()
        else:
            popup("Check your inputs")

    def __addTableSql(self):
        try:
            sqliteConnection = sqlite3.connect("sql.db")
            cursor = sqliteConnection.cursor()
            table = """CREATE TABLE PATIENTS(
                Bill_No TEXT PRIMARY KEY NOT NULL,
                Patient_ID TEXT NOT NULL,
                Date TEXT NOT NULL,
                Time TEXT NOT NULL,
                Name TEXT NOT NULL,
                Age INTEGER NOT NULL,
                Gender TEXT NOT NULL,
                Consultant TEXT NOT NULL,
                Referred_By TEXT NOT NULL,
                Payment TEXT NOT NULL,
                Services TEXT NOT NULL,
                Cost INTEGER NOT NULL,
                Due INTEGER NOT NULL
            )"""
            cursor.execute(table)
            sqliteConnection.commit()
            popup("Database created")
        except sqlite3.Error as error:
            popup("Error occured: " + str(error))
        finally:
            if sqliteConnection:
                sqliteConnection.close()

    def __delPatientByBillNo(self, billno, labels):
        for i in labels:
            i.destroy()
        try:
            db = sqlite3.connect("sql.db")
            cursor = db.cursor()
            delete = """DELETE FROM PATIENTS WHERE Bill_No=?"""
            cursor.execute(delete, (billno,))
            db.commit()
        except sqlite3.Error as error:
            popup("Error occured: " + str(error))
        finally:
            db.close()

    def __addToTable(
        self,
        billno,
        pid,
        name,
        age,
        gender,
        consultant,
        referred,
        payment,
        treatment,
        cost,
        due,
    ):
        global table_row_count
        if(table_row_count == 7):
            self.TableFrame.destroy()
            self.__initTableFrame()
            table_row_count = 1

        col1_temp = Label(
            self.TableFrame,
            font=("arial", 10),
            relief="groove",
            text=billno,
            borderwidth=1,
            width=10,
            padx=2,
            pady=9,
        )
        col1_temp.grid(row=table_row_count, column=0, padx=(40, 0))
        col2_temp = Label(
            self.TableFrame,
            font=("arial", 10),
            relief="groove",
            text=pid,
            borderwidth=1,
            width=10,
            padx=2,
            pady=9,
        )
        col2_temp.grid(row=table_row_count, column=1)
        col3_temp = Label(
            self.TableFrame,
            font=("arial", 10),
            relief="groove",
            text=name,
            borderwidth=1,
            width=20,
            padx=2,
            pady=9,
        )
        col3_temp.grid(row=table_row_count, column=2)
        col4_temp = Label(
            self.TableFrame,
            font=("arial", 10),
            relief="groove",
            text=age,
            borderwidth=1,
            width=5,
            padx=2,
            pady=9,
        )
        col4_temp.grid(row=table_row_count, column=3)
        col5_temp = Label(
            self.TableFrame,
            font=("arial", 10),
            relief="groove",
            text=gender,
            borderwidth=1,
            width=10,
            padx=2,
            pady=9,
        )
        col5_temp.grid(row=table_row_count, column=4)
        col6_temp = Label(
            self.TableFrame,
            font=("arial", 10),
            relief="groove",
            text=consultant,
            borderwidth=1,
            width=50,
            anchor="w",
            padx=2,
            pady=9,
        )
        col6_temp.grid(row=table_row_count, column=5)
        col7_temp = Label(
            self.TableFrame,
            font=("arial", 10),
            relief="groove",
            text=referred,
            borderwidth=1,
            width=50,
            anchor="w",
            padx=2,
            pady=9,
        )
        col7_temp.grid(row=table_row_count, column=6)
        col8_temp = Label(
            self.TableFrame,
            font=("arial", 10),
            relief="groove",
            text=payment,
            borderwidth=1,
            width=10,
            padx=2,
            pady=9,
        )
        col8_temp.grid(row=table_row_count, column=7)
        col9_temp = Label(
            self.TableFrame,
            font=("arial", 10),
            relief="groove",
            text=treatment,
            borderwidth=1,
            width=59,
            padx=2,
            pady=9,
        )
        col9_temp.grid(row=table_row_count + 1, column=0, columnspan=5, padx=(40, 0))
        col10_temp = Label(
            self.TableFrame,
            font=("arial", 10),
            relief="groove",
            text=f"Cost: {cost}",
            borderwidth=1,
            width=50,
            padx=2,
            pady=9,
        )
        col10_temp.grid(row=table_row_count + 1, column=5)
        col11_temp = Label(
            self.TableFrame,
            font=("arial", 10),
            relief="groove",
            text=f"Due: {due}",
            borderwidth=1,
            width=50,
            padx=2,
            pady=9,
        )
        col11_temp.grid(row=table_row_count + 1, column=6)
        col12_temp = Label(
            self.TableFrame,
            borderwidth=1,
            width=10,
            padx=2,
            pady=2,
        )
        col12_temp.grid(row=table_row_count + 1, column=7)
        col_btn = Button(
            col12_temp,
            font=("arial", 10),
            text="Delete",
            bg="red",
            fg="white",
            width=8,
            command=lambda: self.__delPatientByBillNo(
                billno,
                [
                    col1_temp,
                    col2_temp,
                    col3_temp,
                    col4_temp,
                    col5_temp,
                    col6_temp,
                    col7_temp,
                    col8_temp,
                    col9_temp,
                    col10_temp,
                    col11_temp,
                    col12_temp,
                ],
            ),
        )
        col_btn.pack()
        table_row_count += 2


if __name__ == "__main__":
    root = Tk()
    obj = opd(root)
    root.mainloop()
