from tkinter import *
from tkinter import ttk, messagebox
from functools import partial
from tkinter import filedialog
from tkinter import messagebox
import tkinter
from tkcalendar import Calendar, DateEntry
from pathlib import Path
import os
import sys
from sys import platform
from subprocess import Popen, check_call
import git
import warnings
import shutil
from dotenv import load_dotenv, dotenv_values
from datetime import datetime, timedelta, date, time
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning)
if platform == "linux" or platform == "linux2":
    pass
elif platform == "win32":
	from subprocess import CREATE_NEW_CONSOLE
import json
VERSION = "1.0"
OWNER = ""
def run_module(comlist):
	if platform == "linux" or platform == "linux2":
		comlist[:0] = ["--"]
		comlist[:0] = ["gnome-terminal"]
		# print(comlist)
		Popen(comlist)
	elif platform == "win32":
		Popen(comlist, creationflags=CREATE_NEW_CONSOLE)
	
	comall = ''
	for com in comlist:
		comall += com + " "
	print(comall)

def main():
	window = Window()
	window.mainloop()

class Window(Tk):
	def __init__(self) -> None:
		super().__init__()
		
		self.title(f'{OWNER} {VERSION}')
		# self.resizable(0, 0)
		self.grid_propagate(False)
		width = 550
		height = 350
		swidth = self.winfo_screenwidth()
		sheight = self.winfo_screenheight()
		newx = int((swidth/2) - (width/2))
		newy = int((sheight/2) - (height/2))
		self.geometry(f"{width}x{height}+{newx}+{newy}")
		self.columnconfigure(0, weight=1)
		# self.columnconfigure(1, weight=1)
		# self.columnconfigure(2, weight=1)
		# self.columnconfigure(3, weight=1)

		self.rowconfigure(0, weight=1)
		# self.rowconfigure(1, weight=1)
		# self.rowconfigure(2, weight=1)
		
		exitButton = ttk.Button(self, text="Exit", command=lambda:self.procexit())
		pullButton = ttk.Button(self, text='Update Script', command=lambda:self.gitPull())
		# settingButton = ttk.Button(self, text='Chrome Profiles Setup', command=lambda:self.chromeProfile())
		
		exitButton.grid(row=2, column=3, sticky=(E), padx=20, pady=5)
		pullButton.grid(row = 2, column = 0, sticky = (W), padx=20, pady=10)
		# settingButton.grid(row = 2, column = 0, sticky = (W), padx=20, pady=10)

		mainFrame = MainFrame(self)
		mainFrame.grid(column=0, row=0, sticky=(N, E, W, S), columnspan=4)

	def gitPull(self):
		git_dir = os.getcwd() 
		g = git.cmd.Git(git_dir)
		g.pull()		
		messagebox.showinfo(title='Info', message='the scripts has updated..')


	def procexit(self):
		try:
			for p in Path(".").glob("__tmp*"):
				p.unlink()
		except:
			pass
		sys.exit()

class MainFrame(ttk.Frame):
	def __init__(self, window) -> None:
		super().__init__(window)
		# configure
		# self.grid(column=0, row=0, sticky=(N, E, W, S), columnspan=2)
		framestyle = ttk.Style()
		framestyle.configure('TFrame', background='#C1C1CD')
		self.config(padding="20 20 20 20", borderwidth=1, relief='groove', style='TFrame')
		
		# self.place(anchor=CENTER)
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		self.rowconfigure(2, weight=1)
		self.rowconfigure(3, weight=1)
		self.rowconfigure(4, weight=1)
		self.rowconfigure(5, weight=1)
		self.rowconfigure(6, weight=1)
		self.rowconfigure(7, weight=1)
		self.rowconfigure(8, weight=1)
		self.rowconfigure(9, weight=1)
		self.rowconfigure(10, weight=1)
  
		
		titleLabel = TitleLabel(self, 'Main Menu')
		cellHunterButton = FrameButton(self, window, text="cell hunter", class_frame=CellHunterFrame)
		captchaTokenButton = FrameButton(self, window, text="Update ReCaptcha Token", class_frame=RecaptchaTokenFrame)

		# layout
		titleLabel.grid(column = 0, row = 0, sticky=(W, E, N, S), padx=15, pady=5, columnspan=4)
		cellHunterButton.grid(column = 0, row = 1, sticky=(W, E, N, S), padx=15, pady=5)
		captchaTokenButton.grid(column = 0, row = 2, sticky=(W, E, N, S), padx=15, pady=5)


class TitleLabel(ttk.Label):
	def __init__(self, parent, text):
		super().__init__(parent)
		font_tuple = ("Comic Sans MS", 20, "bold")
		self.config(text=text, font=font_tuple, anchor="center")

class FrameButton(ttk.Button):
	def __init__(self, parent, window, **kwargs):
		super().__init__(parent)
		# object attributes
		self.text = kwargs['text']
		# configure
		self.config(text = self.text, command = lambda : kwargs['class_frame'](window))

class CellHunterFrame(ttk.Frame):
	def __init__(self, window) -> None:
		super().__init__(window)
		# configure
		self.grid(column=0, row=0, sticky=(N, E, W, S), columnspan=4)
		self.config(padding="20 20 20 20", borderwidth=1, relief='groove')
		self.columnconfigure(0, weight=1)

		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		self.rowconfigure(2, weight=1)
		self.rowconfigure(3, weight=1)
		self.rowconfigure(4, weight=1)
		self.rowconfigure(5, weight=1)

		# populate
		titleLabel = TitleLabel(self, text="Cells Hunter")
		closeButton = CloseButton(self)
		
		labelcellids = Label(self, text="CELL ID's:")
		textcellids = Entry(self, width=50, )
		labeldate = Label(self, text="Click Date:")
		textdate = DateEntry(self, width= 20, date_pattern='yyy-mm-dd')
		labeltime = Label(self, text="Click Time:")
		texttime = Entry(self, width=15)

		runButton = ttk.Button(self, text='Run Process', command = lambda:self.run_process(date=textdate, time=texttime, cellids=textcellids))

		# layout
		titleLabel.grid(column = 0, row = 0, sticky = (W, E, N, S))
		labeldate.grid(column = 0, row = 1, sticky=(W))
		textdate.grid(column=0, row=1)
		labeltime.grid(column = 0, row = 2, sticky=(W))
		texttime.grid(column=0, row=2)
		texttime.insert(0, os.environ.get("CLICKTIME"))
        
		labelcellids.grid(column = 0, row = 3, sticky=(W))
		textcellids.grid(column=0, row=3)
		runButton.grid(column = 0, row = 3, sticky = (E))
		closeButton.grid(column = 0, row = 6, sticky = (E, N, S))

	def run_process(self, **kwargs):
		try:
			date.fromisoformat(kwargs['date'].get())
		except ValueError:
			raise ValueError("Incorrect date format, should be YYYY-MM-DD")
		try:
			time.fromisoformat(kwargs['time'].get())
		except ValueError:
			raise ValueError("Incorrect time format, should be HH:MM:SS.MS")
		
		comlist = [PYLOC, "miner.py", "-d", kwargs['date'].get(), "-t", kwargs['time'].get(), "-c", kwargs['cellids'].get()]
		run_module(comlist=comlist)

class RecaptchaTokenFrame(ttk.Frame):
	def __init__(self, window) -> None:
		super().__init__(window)
		# configure
		self.grid(column=0, row=0, sticky=(N, E, W, S), columnspan=4)
		self.config(padding="20 20 20 20", borderwidth=1, relief='groove')
		self.columnconfigure(0, weight=1)

		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		self.rowconfigure(2, weight=1)
		self.rowconfigure(3, weight=1)
		self.rowconfigure(4, weight=1)
		self.rowconfigure(5, weight=1)

		# populate
		check = Path("captcharesponse.txt")
		if not check.is_file():
			with open('captcharesponse.txt', 'w') as fp:
				pass
				
		texttoken = Text(self, height = 10, width = 75)
		with open("captcharesponse.txt", "r") as file:
			content = file.readlines()
		# breakpoint()
		texttoken.insert(INSERT, content)
		closeButton = CloseButton(self)
		saveButton = ttk.Button(self, text='Save', command = lambda:self.save(content=texttoken))
		texttoken.grid(column = 0, row = 1, sticky=(W))
		closeButton.grid(column = 0, row = 6, sticky = (E, N, S))
		saveButton.grid(column = 0, row = 6, sticky = (W, N, S))

    
	def save(self, **kwargs):
		# breakpoint()
		with open("captcharesponse.txt", "w") as file:
			file.write(kwargs['content'].get("1.0",'end-1c'))
		messagebox.showinfo(title='Info', message='ReCaptcha Token Saved..')
class CloseButton(ttk.Button):
	def __init__(self, parent):
		super().__init__(parent)
		self.config(text = '< Back', command=lambda : parent.destroy())

if __name__ == "__main__":
	load_dotenv()
	
	if platform == "linux" or platform == "linux2":
		PYLOC = "python"
	elif platform == "win32":
		PYLOC = os.environ.get("PYLOC")
	main()