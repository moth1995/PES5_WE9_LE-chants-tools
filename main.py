import csv
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path

def read_data(file_to_read,pos,grab):
    with open(file_to_read,"rb") as opened_file:
        opened_file.seek(pos,0)
        grabed_data=opened_file.read(grab)
    return grabed_data

def to_dec(var):
    var1=int.from_bytes(var,"little")
    return var1

def tobytes(import_var):
    import_var1=(import_var).to_bytes(2,byteorder="little")
    return import_var1

def make_backup():
    with open(root.filename,"rb") as rf_exe:
        chunk_size=4096
        with open(Path(root.filename).stem+".bak","wb") as wf_exe:
            rf_exe_chunk = rf_exe.read(chunk_size)
            while len(rf_exe_chunk) >0:
                wf_exe.write(rf_exe_chunk)
                rf_exe_chunk = rf_exe.read(chunk_size)

def get_team_names(x):
    offset=0x6E2A70
    baseaddress=4194304
    if Path(root.filename).stat().st_size ==22793412:
        offset=0x6E07A8
        baseaddress=4200960
    nameoffset=int.from_bytes(read_data(root.filename,offset+(x*16),0x4),"little")-baseaddress
    with open(root.filename,"rb") as opened_file:
        opened_file.seek(nameoffset,0)
        name=b''
        grabed_data=opened_file.read(1)
        while grabed_data!=b'\x00':
            name+=grabed_data
            grabed_data=opened_file.read(1)
        #print(name.decode('utf-8'))
    name=name.decode('utf-8')
    return name

def create_map():
    if root.filename=="":
        messagebox.showinfo(title=app_name, message="Please first select a PES5/WE9/LE executable")
    else:
        try:
            #the first value for offset is for PES5/WE9/LE
            offset=0x6DF128
            #if the file is bigger then is a we9le and we have to change the offset
            if Path(root.filename).stat().st_size ==22793412:
                offset=0x6DCED8
            with open(Path(root.filename).stem+" chants map" + ".csv", "w",newline="",encoding="utf-8") as f:
                csv_escribir = csv.writer(f)
                csv_escribir.writerow(["Team ID","BIN ID","AFS FILE","Team Name"])
            for count in range (0,221):
                x=to_dec(read_data(root.filename,offset+(count*4),0X2))
                y=to_dec(read_data(root.filename,offset+(count*4)+2,0X2))
                afs_file=""
                if y==0:
                    afs_file="0_sound.afs"
                elif y==1:
                    afs_file="0_text.afs"
                elif y==2:
                    afs_file="x_sound.afs"
                elif y==3:
                    afs_file="x_text.afs"
                with open(Path(root.filename).stem+" chants map" + ".csv", "a+",newline="", encoding="utf-8") as f:
                    csv_escribir = csv.writer(f)
                    csv_escribir.writerow([count,x,afs_file,get_team_names(count)])
            messagebox.showinfo(title=app_name, message="Map created successfully")
        except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
            messagebox.showerror(title=app_name, message="Error al generar mapa")

def import_map():
    if root.filename=="":
        messagebox.showinfo(title=app_name, message="Please first select a PES5/WE9/LE executable")
    else:
        csvsearched=filedialog.askopenfilename(initialdir=".",title="Select a CSV file", filetypes=[("CSV file", "*.csv")])
        try:
            if backup_check.get():
                make_backup()
            with open(csvsearched,"r", newline="") as csvfile:
                csvdata = csv.reader(csvfile)
                #we skip the header
                next(csvdata)
                import_ok=False
                for col in csvdata:
                    if col[2]=="0_sound.afs" or col[2]=="0_text.afs" or col[2]=="x_sound.afs" or col[2]=="x_text.afs":
                        afs_file=0
                        if col[2]=="0_sound.afs":
                            afs_file=0
                        elif col[2]=="0_text.afs":
                            afs_file=1
                        elif col[2]=="x_sound.afs":
                            afs_file=2
                        elif col[2]=="x_text.afs":
                            afs_file=3
                        try:
                            with open(root.filename,"r+b") as opened_file:
                                #the first value for offset is for PES5/WE9
                                offset=0x6DF128
                                #if the file is bigger then is a WE9LE and we have to change the offset
                                if Path(root.filename).stat().st_size ==22793412:
                                    offset=0x6DCED8
                                opened_file.seek(offset+(int(col[0])*4),0)
                                opened_file.write(tobytes(int(col[1])))
                                opened_file.seek(offset+(int(col[0])*4)+2,0)
                                opened_file.write(tobytes(afs_file))
                            import_ok=True
                        except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
                            messagebox.showerror(title=app_name, message="Error while saving PES5/WE9/LE.exe\nplease run this program as administrator")
                            import_ok=False
                            break
                    else:
                        messagebox.showerror(title=app_name, message="Error with csv file please check \"AFS FILE\" column")
                        break
                if import_ok:
                    messagebox.showinfo(title=app_name, message="Map import successfully")
        except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
            messagebox.showerror(title=app_name, message="Error while reading map")
def search_exe():
    global my_label
    my_label.destroy()
    try:
        root.filename=filedialog.askopenfilename(initialdir=".",title="Select a PES5/WE9/LE Executable", filetypes=[("PES5/WE9/LE Executable", "*.exe")])
        #print(Path(root.filename).stat().st_size)
        my_label= Label(root, text=root.filename)
        my_label.place(x=0,y=180)
    except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
        #si no selecciono ningun ejecutable volvemos a setear la variable en vacio y damos mensaje de error
        root.filename=""
        messagebox.showerror(title=app_name, message="Select a PES5/WE9/LE.exe")


app_name="PES5/WE9/LE Chants Tool"
root = Tk()
root.title(app_name)
#root.geometry("400x200")
w = 400 # width for the Tk root
h = 200 # height for the Tk root
# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen
# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
# set the dimensions of the screen 
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
root.filename=""
my_btn= Button(root, text="Select a PES5/WE9/LE.exe", command=search_exe)
my_btn1= Button(root, text="Create chants map", command=create_map)
my_btn2= Button(root, text="Import chants map", command=import_map)
backup_check=IntVar()
checkbox_backup=Checkbutton(root, text="Make backup of PES5/WE9/LE.exe",variable=backup_check)
my_label= Label(root)
my_btn.place(relx=0.5, rely=0.5, anchor=CENTER)
my_btn1.place(x=220,y=150)
my_btn2.place(x=70,y=150)
checkbox_backup.place(x=60,y=120)
root.resizable(False, False)
root.mainloop()