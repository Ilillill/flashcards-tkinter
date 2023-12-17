import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import sqlite3
from tkinter import messagebox
import pandas as pd
import pickle
import random
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

try:
    with open("./database_data.dat", "rb") as file:
        database_name = pickle.load(file)
except:
    database_name = ''

COLOUR_WHITE = "#FDFFF0"
COLOUR_GREEN = "#A1DD70"
COLOUR_RED = "#A23131"
COLOUR_FRAME = "#E8ECD6"
flashcards = []
flashcards_temp = []

def create_database():
    try:
        database_path = filedialog.asksaveasfilename(title="Create Database", initialdir="./assets/", defaultextension="db", filetypes=(("Database files *.db", "*.db"), ("All files", "*.*")))
    except (AttributeError, FileNotFoundError):
        return
    if len(database_path) != 0:
        file_path = filedialog.askopenfilename(initialdir="./", title='Select CSV file', filetypes=(("CSV files","*.csv"),))
        try:
            content = pd.read_csv(file_path)
            connection = sqlite3.connect(database_path)
            content.to_sql("data", con=connection)
            connection.commit()
            connection.close()

            database_name = database_path
            with open("./database_data.dat", "wb") as dumpfile:
                    pickle.dump(database_name, dumpfile)
            get_15_flashcards()
            Flashcards(root)
        except:
            return

def get_15_flashcards():
    global flashcards
    global flashcards_temp
    flashcards = []
    flashcards_temp = []
    flashcards_number = 15
    flashcards_from_database = []
    selected_three_star_flashcards = []
    selected_two_star_flashcards = []
    selected_one_star_flashcards = []
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM data",)
    total_number_of_flashcards = [n_rows[0] for n_rows in cursor.fetchall()][0]
    cursor.execute("SELECT COUNT(*) FROM data WHERE Stars = 0",)
    one_star_flashcards = [n_rows[0] for n_rows in cursor.fetchall()][0]
    cursor.execute("SELECT COUNT(*) FROM data WHERE Stars = 1",)
    two_star_flashcards = [n_rows[0] for n_rows in cursor.fetchall()][0]
    cursor.execute("SELECT COUNT(*) FROM data WHERE Stars = 2",)
    three_star_flashcards = [n_rows[0] for n_rows in cursor.fetchall()][0]
    if total_number_of_flashcards != 0:
        if total_number_of_flashcards < 15:
            cursor.execute("SELECT * FROM data ORDER BY RANDOM() LIMIT 15",)
            flashcards_from_database = [[row[0], row[1], row[2], row[3]] for row in cursor.fetchall()]
        else:
            if three_star_flashcards != 0:
                if three_star_flashcards < 2:
                    cursor.execute(f"SELECT * FROM data WHERE Stars = 2 ORDER BY RANDOM() LIMIT {three_star_flashcards}",)
                    selected_three_star_flashcards = [[row[0], row[1], row[2], row[3]] for row in cursor.fetchall()]
                    flashcards_number -= 1
                else:
                    cursor.execute("SELECT * FROM data WHERE Stars = 2 ORDER BY RANDOM() LIMIT 2",)
                    selected_three_star_flashcards = [[row[0], row[1], row[2], row[3]] for row in cursor.fetchall()]
                    flashcards_number -= 2
            if two_star_flashcards != 0:
                if two_star_flashcards < 3:
                    cursor.execute(f"SELECT * FROM data WHERE Stars = 1 ORDER BY RANDOM() LIMIT {two_star_flashcards}",)
                    selected_two_star_flashcards = [[row[0], row[1], row[2], row[3]] for row in cursor.fetchall()]
                    flashcards_number -= two_star_flashcards
                else:
                    cursor.execute("SELECT * FROM data WHERE Stars = 1 ORDER BY RANDOM() LIMIT 3",)
                    selected_two_star_flashcards = [[row[0], row[1], row[2], row[3]] for row in cursor.fetchall()]
                    flashcards_number -= 3
            if one_star_flashcards != 0:
                if one_star_flashcards < flashcards_number:
                    cursor.execute(f"SELECT * FROM data WHERE Stars = 0 ORDER BY RANDOM() LIMIT {one_star_flashcards}",)
                    selected_one_star_flashcards = [[row[0], row[1], row[2], row[3]] for row in cursor.fetchall()]
                else:
                    cursor.execute(f"SELECT * FROM data WHERE Stars = 0 ORDER BY RANDOM() LIMIT {flashcards_number}",)
                    selected_one_star_flashcards = [[row[0], row[1], row[2], row[3]] for row in cursor.fetchall()]
                flashcards_number -= len(selected_one_star_flashcards)
            flashcards_from_database = selected_three_star_flashcards + selected_two_star_flashcards + selected_one_star_flashcards
    else:
        create_database()
    random.shuffle(flashcards_from_database)
    connection.close()
    flashcards = flashcards_from_database
    return flashcards

def open_database():
    global database_name
    new_database_path = filedialog.askopenfilename(initialdir="./", title='Open database', filetypes=(("Database files *.db", "*.db"), ("All files", "*.*")))
    try:
        if new_database_path != '':
            database_name = new_database_path
            with open("./database_data.dat", "wb") as dumpfile:
                    pickle.dump(database_name, dumpfile)
            get_15_flashcards()
            Flashcards(root)
    except:
        return

def reset_all_stars():
    if messagebox.askyesno(title="Clear stars", message="Are you sure you want to clear all progress?"):
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute(f'UPDATE data SET Stars=?', (0,))
        connection.commit()
        connection.close()
        get_15_flashcards()
        Flashcards(root)

def display_resources(option):
    popup_window = tk.Toplevel()
    popup_window.geometry("800x800+1400+500")
    popup_window.configure(bg='white')
    popup_window.columnconfigure(0, weight=1)
    popup_window.rowconfigure(0, weight=1
    )
    text_entry = tk.Text(popup_window, font=('Calibri', 10))
    text_entry.grid(row=0, column=0, sticky='news')
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    if option == 0:
        cursor.execute(f"SELECT * FROM data WHERE Stars = 0",)
        popup_window.title("One star flashcards")
    elif option == 1:
        cursor.execute(f"SELECT * FROM data WHERE Stars = 1",)
        popup_window.title("Two star flashcards")
    elif option == 2:
        cursor.execute(f"SELECT * FROM data WHERE Stars = 2",)
        popup_window.title("Three star flashcards")
    else:
        cursor.execute(f"SELECT * FROM data",)
        popup_window.title("All flashcards")
    flashcards_list = [[row[0], row[1], row[2], row[3]] for row in cursor.fetchall()]
    position = 1
    for card in flashcards_list:
        txt = f"⋯ {card[1]}\t-\t{card[2]}\n"
        text_entry.insert(f"{position}.0", txt)
        position += 1
    scrollbar = ttk.Scrollbar(popup_window, orient='vertical', command=text_entry.yview)
    scrollbar.grid(row=0, column=1, sticky="NS")
    text_entry["yscrollcommand"] = scrollbar.set
    connection.close()

def display_instructions():
    popup_window = tk.Toplevel()
    popup_window.geometry("800x700+1400+500")
    popup_window.configure(bg=COLOUR_WHITE)

    instructions_message = f'''
    CREATE CSV FILES:\n
    Open Google Sheets -> Create 3 columns:\n
    First column: Questions, Second column: Answers, Third column: Stars\n
    It is very important to leave the name as 'stars' and populate values with 0 (number zero)\n\n

    CREATE A NEW DATABASE AND ADD A CSV FILE\n
    Go to options and select 'Create new flashcards from CSV'\n
    In the first popup window select location and name for your Flascards database.\n 
    In the second popup window select the previously created CSV file.\n\n 

    SWAP BETWEEN EXISTING FLASHCARD DATABASES\n 
    Go to options and select 'Open existing flashcards database'\n 
    Open one of previously created database files.

    '''
    instructions_label = tk.Label(popup_window, text=instructions_message, bg=COLOUR_WHITE, font=('Calibri', 10))
    instructions_label.grid(row=0, column=0, sticky='news')

class OptionsFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.grid(row=0, column=0, sticky='news')
        self.configure(bg=COLOUR_WHITE)
        self.columnconfigure(0, weight=1)
        bt_create_new_database = ttk.Button(self, text='Create new flashcards from CSV', width=100, command=lambda: create_database())
        bt_create_new_database.grid(row=0, column=0, padx=40, pady=(140, 5))
        bt_select_database = ttk.Button(self, text='Open existing flashcards database', width=100, command=lambda: open_database())
        bt_select_database.grid(row=1, column=0, padx=40, pady=15)

        if database_name != '':
            ttk.Separator(self).grid(row=2, column=0, sticky='ew', padx=40, pady=40)
            bt_all_flashcards = ttk.Button(self, text='Display all flashcards', width=100, command=lambda: display_resources('all'))
            bt_all_flashcards.grid(row=3, column=0, padx=40, pady=15)
            bt_star_1 = ttk.Button(self, text='Display ⭐ flashcards', width=100, command=lambda: display_resources(0))
            bt_star_1.grid(row=5, column=0, padx=40, pady=15)
            bt_star_2 = ttk.Button(self, text='Display ⭐⭐ flashcards', width=100, command=lambda: display_resources(1))
            bt_star_2.grid(row=6, column=0, padx=40, pady=15)
            bt_star_3 = ttk.Button(self, text='Display ⭐⭐⭐ flashcards', width=100, command=lambda: display_resources(2))
            bt_star_3.grid(row=7, column=0, padx=40, pady=15)
            bt_star_reset = ttk.Button(self, text='Reset all ⭐', width=100, command=lambda: reset_all_stars())
            bt_star_reset.grid(row=8, column=0, padx=40, pady=15)
            ttk.Separator(self).grid(row=9, column=0, sticky='ew', padx=40, pady=40)
            bt_back = ttk.Button(self, text='Back', width=100, command=lambda: [self.destroy(), Flashcards(root)])
            bt_back.grid(row=10, column=0, padx=40, pady=15)

        ttk.Separator(self).grid(row=11, column=0, sticky='ew', padx=40, pady=40)
        bt_instructions = ttk.Button(self, text='Display instructions', width=100)
        bt_instructions['command'] = lambda: display_instructions()
        bt_instructions.grid(row=12, column=0, padx=40, pady=15)

def draw_flashcard():
    global flashcards
    global flashcards_temp
    if len(flashcards) == 0:
        flashcards = flashcards_temp.copy()
        random.shuffle(flashcards)
        flashcards_temp = []
        current_flashcard = flashcards.pop()
    else:
        current_flashcard = flashcards.pop()
    flashcards_temp.append(current_flashcard)
    return current_flashcard

class Flashcards(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.grid(row=0, column=0, sticky='news')
        self.configure(bg=COLOUR_FRAME)

        self.c_f = draw_flashcard()

        canvas_image = tk.Canvas(self, width=1920, height=930, bg=COLOUR_WHITE, highlightthickness=0)
        canvas_image.grid(row=0, column=0, sticky="ew")
        canvas_image.create_image(0, 0, image=bg_image, anchor="nw")
        question = ''
        if len(self.c_f[1]) < 40:
            question = self.c_f[1]
        else:
            question = f"{self.c_f[1][:40]}\n{self.c_f[1][40:]}"
        text_bg = canvas_image.create_text(960, 450, text=question, font=('Calibri', 40))
        text_fg = canvas_image.create_text(962, 452, text=question, font=('Calibri', 40), fill=COLOUR_GREEN)

        ''' STARS ⭐⭐⭐⭐⭐ '''
        complete_list = flashcards + flashcards_temp
        cards_0 = 0
        cards_1 = 0
        cards_2 = 0
        for card in complete_list:
            if card[3] == 0:
                cards_0 += 1
            elif card[3] == 1:
                cards_1 += 1
            elif card[3] == 2:
                cards_2 += 1
        text_progress = f"{cards_0} ⭐ | {cards_1} ⭐⭐ | {cards_2} ⭐⭐⭐"
        text_progress_canvas = canvas_image.create_text(300, 840, text='', font=('Calibri', 14), fill='black')
        canvas_image.itemconfig(text_progress_canvas, text=text_progress)
        star_1_bg = canvas_image.create_text(170, 115, text="⭐", font=('Calibri', 44), fill='black')
        star_1_fg = canvas_image.create_text(170, 115, text="⭐", font=('Calibri', 40), fill='yellow')
        if self.c_f[3] == 0:
            star_2_bg = canvas_image.create_text(270, 115, text="⭐", font=('Calibri', 44), fill='black')
            star_2_fg = canvas_image.create_text(270, 115, text="⭐", font=('Calibri', 40), fill='white')
            star_3_bg = canvas_image.create_text(370, 115, text="⭐", font=('Calibri', 44), fill='black')
            star_3_fg = canvas_image.create_text(370, 115, text="⭐", font=('Calibri', 40), fill='white')
        elif self.c_f[3] == 1:
            star_2_bg = canvas_image.create_text(270, 115, text="⭐", font=('Calibri', 44), fill='black')
            star_2_fg = canvas_image.create_text(270, 115, text="⭐", font=('Calibri', 40), fill='yellow')
            star_3_bg = canvas_image.create_text(370, 115, text="⭐", font=('Calibri', 44), fill='black')
            star_3_fg = canvas_image.create_text(370, 115, text="⭐", font=('Calibri', 40), fill='white')
        elif self.c_f[3] == 2:
            star_2_bg = canvas_image.create_text(270, 115, text="⭐", font=('Calibri', 44), fill='black')
            star_2_fg = canvas_image.create_text(270, 115, text="⭐", font=('Calibri', 40), fill='yellow')
            star_3_bg = canvas_image.create_text(370, 115, text="⭐", font=('Calibri', 44), fill='black')
            star_3_fg = canvas_image.create_text(370, 115, text="⭐", font=('Calibri', 40), fill='yellow')

        answer = tk.Entry(self, width=95, bg=COLOUR_WHITE, fg=COLOUR_GREEN, justify="center", font=('Calibri', 18))
        answer.grid(row=1, column=0)
        answer.focus()
        answer.bind("<Return>", lambda event: check_answer(self, self.c_f))

        settings = tk.Button(image=OPTIONS_IMAGE, borderwidth=0, relief="flat", activebackground=COLOUR_WHITE, bg=COLOUR_WHITE)
        settings['command'] = lambda: [self.destroy(), OptionsFrame(root)]
        settings_location = canvas_image.create_window(1750, 115, window=settings)

        next = tk.Button(image=NEXT_IMAGE, borderwidth=0, relief="flat", activebackground=COLOUR_WHITE, bg=COLOUR_WHITE)
        next['command'] = lambda: [self.destroy(), Flashcards(root)]
        next_location = canvas_image.create_window(1750, 810, window=next)

        buttons_frame = tk.Frame(self, bg=COLOUR_FRAME, bd=0, borderwidth=0)
        buttons_frame.grid(row=2, column=0, sticky='news')
        buttons_frame.columnconfigure(0, weight=1)

        button_check = tk.Button(buttons_frame, image=CHECK_IMAGE, bg=COLOUR_FRAME, borderwidth=0, relief="flat", activebackground=COLOUR_FRAME)
        button_check["command"] = lambda: check_answer(self, self.c_f)
        button_check.grid(row=0, column=0, sticky='ew', pady=(7, 0))

        def update_progress(self):
            complete_list = flashcards + flashcards_temp
            cards_0 = 0
            cards_1 = 0
            cards_2 = 0
            for card in complete_list:
                if card[3] == 0:
                    cards_0 += 1
                elif card[3] == 1:
                    cards_1 += 1
                elif card[3] == 2:
                    cards_2 += 1
            text_progress = f"{cards_0} ⭐ | {cards_1} ⭐⭐ | {cards_2} ⭐⭐⭐"
            canvas_image.itemconfig(text_progress_canvas, text=text_progress)

        def update_stars(self, number_of_stars):
            if number_of_stars == 0:
                canvas_image.itemconfig(star_2_bg, fill='black')
                canvas_image.itemconfig(star_2_fg, fill='white')
                canvas_image.itemconfig(star_3_bg, fill='black')
                canvas_image.itemconfig(star_3_fg, fill='white')
            elif number_of_stars == 1:
                canvas_image.itemconfig(star_2_bg, fill='black')
                canvas_image.itemconfig(star_2_fg, fill='yellow')
                canvas_image.itemconfig(star_3_bg, fill='black')
                canvas_image.itemconfig(star_3_fg, fill='white')
            elif number_of_stars == 2:
                canvas_image.itemconfig(star_2_bg, fill='black')
                canvas_image.itemconfig(star_2_fg, fill='yellow')
                canvas_image.itemconfig(star_3_bg, fill='black')
                canvas_image.itemconfig(star_3_fg, fill='yellow')

        def answer_good(self, text):
            answer.delete(0, "end")
            canvas_image["bg"] = COLOUR_GREEN
            answer_text = ''
            if len(text[2]) < 40:
                answer_text = text[2]
            else:
                answer_text = f"{text[2][:40]}\n{text[2][40:]}"
            canvas_image.itemconfig(text_bg, text=answer_text)
            canvas_image.itemconfig(text_fg, text=answer_text, fill=COLOUR_WHITE)
            settings['bg'] = COLOUR_GREEN
            next['bg'] = COLOUR_GREEN
            button_check['state'] = 'disabled'
            answer.bind("<Return>", lambda event: [self.destroy(), Flashcards(root)])
            answer['state'] = 'disabled'

        def answer_wrong(self, text):
            canvas_image["bg"] = COLOUR_RED
            if len(text[2]) < 40:
                answer_text = text[2]
            else:
                answer_text = f"{text[2][:40]}\n{text[2][40:]}"
            canvas_image.itemconfig(text_bg, text=answer_text)
            canvas_image.itemconfig(text_fg, text=answer_text, fill=COLOUR_WHITE)


            settings['bg'] = COLOUR_RED
            next['bg'] = COLOUR_RED
            button_check['state'] = 'disabled'
            answer.bind("<Return>", lambda event: [self.destroy(), Flashcards(root)])
            answer['state'] = 'disabled'

        def check_answer(self, current_flashcard):
            user_answer = answer.get().lower()
            if user_answer == str(current_flashcard[2]).lower():
                answer_good(self, current_flashcard)
                if current_flashcard[3] < 2:
                    current_flashcard[3] += 1
            else:
                answer_wrong(self, current_flashcard)
                if current_flashcard[3] != 0:
                    current_flashcard[3] -= 1
        
            connection = sqlite3.connect(database_name)
            cursor = connection.cursor()
            cursor.execute(f'UPDATE data SET Stars=? WHERE rowid={current_flashcard[0]}', (current_flashcard[3],))
            connection.commit()
            connection.close()
            update_stars(self, current_flashcard[3])
            update_progress(self)

root = tk.Tk()
root.title("Flashy ⚡")
root.resizable(False, False)
root.geometry("1920x1080+960+540")
root.configure(bg=COLOUR_FRAME)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

bg_image = tk.PhotoImage(file="./assets/transparent.png")
OPTIONS_IMAGE = tk.PhotoImage(file="./assets/options.png")
CHECK_IMAGE = tk.PhotoImage(file="./assets/check.png")
PASS_IMAGE = tk.PhotoImage(file="./assets/pass.png")
NEXT_IMAGE = tk.PhotoImage(file="./assets/next.png")

if database_name != '':
    try:
        get_15_flashcards()
        Flashcards(root)
    except:
        OptionsFrame(root)    
else:
    OptionsFrame(root)

root.mainloop()
