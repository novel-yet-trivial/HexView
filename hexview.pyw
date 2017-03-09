#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hexview.pyw
#

try:
	import Tkinter as tk
	import ttk
	from tkFileDialog import askopenfile
	from itertools import imap
	python2 = True
	print("python2 detected")
except ImportError:
	import tkinter as tk
	from tkinter import ttk
	from tkinter.filedialog import askopenfile
	python2 = False
	print("python3 detected")

class ScrolledText(tk.Frame):
	def __init__(self, master=None, **kwargs):
		tk.Frame.__init__(self, master, **kwargs)
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		self.txt = tk.Text(self, wrap='none')
		self.txt.grid(row=0, column=0, sticky='nsew')
		vsb = tk.Scrollbar(self, command=self.txt.yview)
		vsb.grid(row=0, column=1, sticky='ns')
		self.txt.config(yscrollcommand=vsb.set)
		hsb = tk.Scrollbar(self, orient='horizontal', command=self.txt.xview)
		hsb.grid(row=1, column=0, sticky='ew')
		self.txt.config(xscrollcommand=hsb.set)
		self.txt.tag_config("odd_row", foreground="blue")

	def set(self, data):
		'''data needs to be a 2D iter of integers'''
		self.txt.delete(1.0, tk.END)
		for line in data:
			for idx, char in enumerate(line):
				char = "{:0>2X} ".format(char)
				if idx%2:
					self.txt.insert(tk.CURRENT, char)
				else:
					self.txt.insert(tk.CURRENT, char, 'odd_row')
			self.txt.delete(tk.CURRENT+"-1c") # delete the trailing space
			self.txt.insert(tk.CURRENT, '\n')

class GUI(tk.Frame):
	def __init__(self, master=None, **kwargs):
		tk.Frame.__init__(self, master, **kwargs)
		self.data = None
		btn_frame = tk.Frame(self)
		btn_frame.pack(anchor=tk.W)
		btn = ttk.Button(btn_frame, text="Load File", command=self.load_file)
		btn.pack(side=tk.LEFT)
		lbl = tk.Label(btn_frame, text="width in bytes:")
		lbl.pack(side=tk.LEFT)
		self.width = tk.IntVar(self, 1024)
		self.width.trace('w', self.chg_width)
		ent = ttk.Entry(btn_frame, textvariable=self.width, width=7)
		ent.pack(side=tk.LEFT)
		self.status = tk.StringVar(self, "")
		ttk.Style().configure('red.TLabel', foreground='red')
		lbl = ttk.Label(btn_frame, style='red.TLabel', textvariable=self.status)
		lbl.pack(side=tk.LEFT)

		self.txt = ScrolledText(self)
		self.txt.pack(fill=tk.BOTH, expand=True)

	def chg_width(self, *args):
		self.status.set(self._chg_width() or '')

	def _chg_width(self):
		if self.data is None:
			return 'Load some data'
		try:
			width = self.width.get()
		except (ValueError, tk.TclError):
			return 'Not a valid integer'
		if width < 1:
			return 'Must be 1 or greater'
		chunks = (self.data[i:i+width] for i in range(0,len(self.data),width))
		if python2: # python2 needs to cast to integers
			chunks = (imap(ord, chunk) for chunk in chunks)
		self.txt.set(chunks)

	def load_file(self, *args):
		f = askopenfile('rb')
		if f is not None:
			self.data = f.read()
			f.close()
		self.chg_width()

def main():
	root = tk.Tk()
	root.title('computerforensicsGWU rules!')
	win = GUI(root)
	win.pack(fill=tk.BOTH, expand=True)
	root.mainloop()

if __name__ == '__main__':
	main()
