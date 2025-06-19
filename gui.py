#imports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from bs4 import BeautifulSoup
import requests
import main
from multiprocessing import Process

#vars
url="https://exam.bujhansi.ac.in/frmViewCampusCurrentResult.aspx?cd=MwA3ADkA"
page=requests.get(url)


soup=BeautifulSoup(page.text,"html.parser")
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
	roll = roll_entry.get()
	result = result_type.get()
	course_selected = course.get()    
	
	if not roll.strip():
		messagebox.showerror("Input Error", "Roll number cannot be empty!")
		return

	msg = f"Roll No: {roll}\nResult Type: {result}\nCourse: {course_selected}"
	messagebox.showinfo("Submitted Data", msg)

	proc=Process(target=main.func,args=(roll,courses[course_selected],resultType[result]))
	proc.start()

def select_all(event):
    event.widget.select_range(0, 'end')
    event.widget.icursor('end')  # Move cursor to end
    return 'break'  # Prevent default behavior



# Main window
root = tk.Tk()
root.title("Student Result Form")
root.geometry("900x400")
root.configure(bg="#f0f2f5")

# Use ttk Style for modern look
style = ttk.Style(root)
style.theme_use('clam')  # Other options: 'alt', 'default', 'classic'
style.configure('TLabel', font=('Helvetica', 12), background='#f0f2f5')
style.configure('TButton', font=('Helvetica', 12), padding=6)
style.configure('TCombobox', font=('Helvetica', 12))

# Frame for padding
frame = ttk.Frame(root, padding=100)
frame.pack(expand=True)

# Roll number input
ttk.Label(frame, text="Roll Number:").grid(row=0, column=0, sticky='w', pady=5)
roll_entry = ttk.Entry(frame, width=30)
roll_entry.grid(row=0, column=1, pady=5,padx=20,sticky='w')
roll_entry.bind('<Control-a>', select_all)

# Dropdown for Result Type
ttk.Label(frame, text="Result Type:").grid(row=1, column=0, sticky='w', pady=5)
result_type = ttk.Combobox(frame, values= list(resultType.keys()), state='readonly', width=30)
result_type.grid(row=1, column=1, pady=5,padx=21, sticky='w')
#result_type.current(0)

# Dropdown for Course
ttk.Label(frame, text="Course: ").grid(row=2, column=0, sticky='w', pady=5)
course = ttk.Combobox(frame, values=list(courses.keys()), state='readonly', width=80)
course.grid(row=2, column=1, pady=5,padx=20,)
#course.current(0)

# Submit Button
submit_btn = ttk.Button(frame, text="Submit", command=submit_form)
submit_btn.grid(row=3, columnspan=2, pady=20)

root.mainloop()
