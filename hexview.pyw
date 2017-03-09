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

def multiple(*func_list):
	'''run multiple functions as one'''
	# I can't decide if this is ugly or pretty
	return lambda *args, **kw: [func(*args, **kw) for func in func_list]; None

def scroll_to_view(scroll_set, *view_funcs):
	''' Allows one widget to control the scroll bar and other widgets
	scroll set: the scrollbar set function
	view_funcs: other widget's view functions
	'''
	def closure(start, end):
		scroll_set(start, end)
		for func in view_funcs:
			func('moveto', start)
	return closure

class ScrolledText(tk.Frame):
	def __init__(self, master=None, **kwargs):
		tk.Frame.__init__(self, master, **kwargs)
		self.columnconfigure(1, weight=1)
		self.rowconfigure(0, weight=1)
		self.lines = tk.Text(self, width=4, wrap='none')
		self.lines.grid(row=0, column=0, sticky='nsew')
		self.txt = tk.Text(self, wrap='none')
		self.txt.grid(row=0, column=1, sticky='nsew')
		vsb = tk.Scrollbar(self, command=multiple(self.txt.yview, self.lines.yview))
		vsb.grid(row=0, column=2, sticky='ns')
		self.txt.config(yscrollcommand=scroll_to_view(vsb.set, self.lines.yview))
		self.lines.config(yscrollcommand=scroll_to_view(vsb.set, self.txt.yview))

		hsb = tk.Scrollbar(self, orient='horizontal', command=self.txt.xview)
		hsb.grid(row=1, column=1, sticky='ew')
		self.txt.config(xscrollcommand=hsb.set)

		self.txt.tag_config("odd_row", foreground="blue")
		self.lines.tag_config("line_num", foreground="red")

	def set_lines(self, width, length):
		self.lines.delete(1.0, tk.END)
		num_width = len(hex(length))-2
		self.lines.config(width=num_width)
		line_nums = ("{:0>{pad}X}".format(i, pad=num_width) for i in range(0, length, width))
		self.lines.insert(1.0, '\n'.join(line_nums), 'line_num')

	def set_with_color(self, data, width, length):
		self.set_lines(width, length)
		self.txt.delete(1.0, tk.END)
		for line_idx, line in enumerate(data):
			for idx, char in enumerate(line):
				char = "{:0>2X} ".format(char)
				if idx%2:
					self.txt.insert(tk.CURRENT, char)
				else:
					self.txt.insert(tk.CURRENT, char, 'odd_row')
			self.txt.delete(tk.CURRENT+"-1c") # delete the trailing space
			self.txt.insert(tk.CURRENT, '\n')
		self.txt.delete(tk.CURRENT+"-1c") # delete the trailing newline

	def set(self, data, width, length):
		'''data needs to be a 2D iter of integers'''
		self.set_lines(width, length)
		self.txt.delete(1.0, tk.END)
		output = []
		for line_idx, line in enumerate(data):
			output.append(" ".join(format(c, '0>2X') for c in line))
		self.txt.insert(tk.CURRENT, '\n'.join(output))

class GUI(tk.Frame):
	def __init__(self, master=None, **kwargs):
		tk.Frame.__init__(self, master, **kwargs)
		self.data = None
		btn_frame = tk.Frame(self)
		btn_frame.pack(anchor=tk.W)
		btn = ttk.Button(btn_frame, text=u"Load File", command=self.load_file)
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
		self.color = tk.IntVar(self, False)
		self.color.trace('w', self.chg_width)
		ckbx = tk.Checkbutton(btn_frame, text='Color', variable=self.color)
		ckbx.pack(side=tk.LEFT)

		self.txt = ScrolledText(self)
		self.txt.pack(fill=tk.BOTH, expand=True)

		self.load_file() # prompt for file at startup

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
		if self.color.get():
			self.txt.set_with_color(chunks, width, len(self.data))
		else:
			self.txt.set(chunks, width, len(self.data))

	def load_file(self, fn=None, *args):
		self.master.withdraw()
		if fn is not None:
			f = open(fn, 'rb')
		else:
			f = askopenfile('rb')
		if f is not None:
			self.data = f.read()
			f.close()
		self.chg_width()
		self.master.deiconify()

def main():
	root = tk.Tk()
	root.title('PyHexView')
	win = GUI(root)
	win.pack(fill=tk.BOTH, expand=True)
	root.mainloop()

if __name__ == '__main__':
	main()
