import tkinter as tk
from tkinter.ttk import Spinbox
from tkinter.colorchooser import askcolor
from tkinter import filedialog, messagebox
import qrcode
from PIL import Image
from rembg import remove
import os
import imghdr

root=tk.Tk()
root.title("QR code generator")
content=tk.StringVar(value="Enter content...")
content_entry=tk.Entry(root, textvariable=content, font=("Times New Roman", 12))
content_entry.pack(padx=5, pady=5, side=tk.TOP)

def del_text(*args):
    if content.get()=="Enter content...":
        content.set("")

def subtle_text(*args):
    if content.get()=="":    
        content.set("Enter content...")

content_entry.bind("<FocusIn>", del_text)
content_entry.bind("<FocusOut>", lambda x: root.after(2000, subtle_text)) # root.after(ms, func) doesn't prevent the main thread from running like time.sleep()

size_frame=tk.Frame(root)
size_frame.pack()

size_lab=tk.Label(size_frame, text="Choose a size: ", font=("Times New Roman", 11))
size_lab.pack(padx=5, pady=5, side=tk.LEFT)

size=tk.IntVar()
size_spinbox=Spinbox(size_frame, from_=1, to=20, textvariable=size, wrap=True, font=("Times New Roman", 11))
size_spinbox.pack(padx=5, pady=5, side=tk.RIGHT)

def choose_color(*args):
    global color
    color=askcolor(title="Color Chooser")   #color[0] is RGB

col_logo_frame=tk.Frame(root)
col_logo_frame.pack()

col_button=tk.Button(col_logo_frame, text="Choose a color", font=("Times New Roman", 10), command=choose_color)
col_button.pack(padx=5, pady=5, side=tk.LEFT)

def choose_logo():
    global path_logo, converted
    converted=False
    path_logo=filedialog.askopenfilename(filetypes=[("PNG files", "*.png"),("JPEG files", "*.jpg"),("GIF files", "*.gif")])
    try:
        if imghdr.what(path_logo) !="png":
            with Image.open(path_logo)as img:
                name=os.path.splitext(os.path.basename(path_logo))[0]
                img.save(name+ ".png")
    except:
        messagebox.showerror("Error", "An error occured selecting your file!")  
        return choose_logo()
    path_logo=str(path_logo.rsplit(".", maxsplit=1)[0])+".png"     
    converted=True

def logo(pil_qr, path):   
    logo_img=Image.open(path_logo).convert("RGBA")
    logo_img=remove(logo_img) # remove bg of logo
    resized_logo=int(pil_qr.size[0]*0.225) # adapted size of logo on top of qr
    logo_img=logo_img.resize((resized_logo, int(resized_logo*logo_img.size[1]/logo_img.size[0]))) # resize logo with same proportions, image filter
    intermediate_status="D:\\Daniel Rabe\\Downloads\\complete_logo.png"
    logo_img.save(intermediate_status) # save changed logo
    complete_logo=Image.open(intermediate_status)
    resized_bg=int(pil_qr.size[0]*0.25) # adapted size of logo on top of qr

    bg=Image.new("RGB", (resized_bg, resized_bg), (255,255,255))
    pos_bg=((resized_bg-complete_logo.size[0])//2, (resized_bg-complete_logo.size[1])//2)
    bg.paste(complete_logo, pos_bg, mask=complete_logo)
    bg=bg.convert("RGBA")
    bg.save(intermediate_status)
    pil_qr=pil_qr.convert("RGBA")
    pil_qr.save(path)
    position=((pil_qr.size[0]-resized_bg)//2, (pil_qr.size[1]-resized_bg)//2) # determine position of logo in qr code
    pil_qr.paste(bg, position, mask=bg) # merge logo and qr
    if converted:
        os.remove(path_logo)
    os.remove(intermediate_status)
    pil_qr.save(path)
    pil_qr.show()

on_off=tk.IntVar()
logo_checkbox=tk.Checkbutton(col_logo_frame, text="Add a custom logo", variable=on_off, font=("Times New Roman", 10), relief=tk.RAISED, onvalue=1, offvalue=0, command=choose_logo)
logo_checkbox.pack(padx=5, pady=5, side=tk.RIGHT)

def qr_code(*args):
    if content.get()=="" or size.get()==0:
        messagebox.showinfo("Information", "Not all necessary components selected.")
        return
    path=filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files","*.jpg")])
    
    qr = qrcode.QRCode(version=size.get()) # change advanced settings, tuple; version (size from 1-40)
    qr.add_data(content.get()) # add the data the qr code should complete_logo
    qr.make(fit=True) # optimize size proportions
    if not("color" in globals()):
        my_qrcode = qr.make_image()
    elif color[0]!=None:    
        my_qrcode = qr.make_image(fill_color=color[0]) # change colors 
    try:       
        my_qrcode.save(path) # save the qr code
    except:
        messagebox.showerror("Error", "An error occured saving your file!")
        return qr_code(*args) 
    if on_off.get()==1:
        my_qrcode=Image.open(path)
        logo(my_qrcode, path)
    else:
        my_qrcode.show()    

gen_button=tk.Button(root, text="Generate QR code", font=("Times New Roman", 12), bitmap="gray12",compound="left", command=qr_code)
gen_button.pack(padx=10, pady=10)

root.mainloop()