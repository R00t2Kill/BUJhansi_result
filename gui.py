#imports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from bs4 import BeautifulSoup
import requests
import main
from multiprocessing import Process
import os



#vars
url="https://exam.bujhansi.ac.in/frmViewCampusCurrentResult.aspx?cd=MwA3ADkA"
# Headers
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
    "Referer": url,
}
if os.path.exists("./src_page"):
	with open("./src_page","r") as fobj:
		pagetext=fobj.read()
else:
	page=requests.get(url,headers=headers,timeout=10)
	pagetext=page.text
	with open("./src_page","w") as fobj:
		fobj.write(pagetext)

soup=BeautifulSoup(pagetext,"html.parser")
ddl_course = soup.find("select", id="ddlCourse")


# Extract all <option> values (skipping the first '-Select-' one)
courses = {}
resultType={"Main":"","Special Back":"6"}

for option in ddl_course.find_all("option")[1:]:  # Skip '-Select-'
	ddlid = option.get("value")
	ddlcourse = option.text.strip()
	courses[ddlcourse]=ddlid







# Function called when Submit is pressed
def submit_form():
	rollfrom = roll_entry_from.get()
	rollto=roll_entry_to.get()
	result = result_type.get()
	course_selected = course.get() 
	print(course_selected)   
	
	if not rollfrom.strip():
		messagebox.showerror("Input Error", "Roll number cannot be empty!")
		return

	msg = f"you can close the window.\n(bg download is supported)."
	messagebox.showinfo("Download started", msg)

	proc=Process(target=main.func,args=(rollfrom,rollto,courses[course_selected],course_selected,resultType[result]))
	proc.start()

def select_all(event):
    event.widget.select_range(0, 'end')
    event.widget.icursor('end')  # Move cursor to end
    return 'break'  # Prevent default behavior



# Main window
root = tk.Tk()
root.title("Student's Result Downloader")
root.geometry("900x600")
root.configure(bg="#f0f2f5")

# Use ttk Style for modern look
style = ttk.Style(root)
style.theme_use('clam')  # Other options: 'alt', 'default', 'classic'
style.configure('TLabel', font=('Helvetica', 12), background='#f0f2f5')
style.configure('TButton', font=('Helvetica', 12), padding=6)
style.configure('TCombobox', font=('Helvetica', 12))

# Frame for padding
frame = ttk.Frame(root, padding=100)
#frame.grid(row=0, column=0, sticky='w', pady=5)
frame.pack(expand =True,fill="both")

#H frame
Hframe = ttk.Frame(frame, padding=10)
Hframe.grid(row=0, column=1, sticky='w', pady=5)


# Roll number input
ttk.Label(frame, text="Roll Number:").grid(row=0, column=0, sticky='w', pady=5)
#first Input field
roll_entry_from = ttk.Entry(Hframe, width=20)
roll_entry_from.grid(row=0, column=0, pady=5,padx=20,sticky='w')
roll_entry_from.bind('<Control-a>', select_all)

ttk.Label(Hframe, text="to").grid(row=0, column=1, sticky='w')

#second Input field
roll_entry_to = ttk.Entry(Hframe, width=20)
roll_entry_to.grid(row=0, column=2, pady=5,padx=20,sticky='w')
roll_entry_to.bind('<Control-a>', select_all)

# Dropdown for Result Type
ttk.Label(frame, text="Result Type:").grid(row=1, column=0, sticky='w', pady=5)
result_type = ttk.Combobox(frame, values= list(resultType.keys()), state='readonly', width=30)
result_type.grid(row=1, column=1, pady=5,padx=21, sticky='w')
#result_type.current(0)

# Dropdown for Course
ttk.Label(frame, text="Course: ").grid(row=2, column=0, sticky='w', pady=5)
course = ttk.Combobox(frame, values=list(courses.keys()), state='readonly', width=80,height=16)
course.grid(row=2, column=1, pady=5,padx=20,)
#course.current(0)

# Submit Button
submit_btn = ttk.Button(frame, text="Download Results", command=submit_form)
submit_btn.grid(row=3, columnspan=2, pady=20)

root.mainloop()
