from Tkinter import *
import tkFileDialog
from gv import Voice
from gv.util import input

LOGLENGTH=10
DEBUG=False

class loginwin:
    def __init__(self):
        self.logged=False
        self.master = Toplevel()
        self.root = Canvas(self.master)
        self.master.title("Google Login")
        self.user=StringVar()
        self.pw=StringVar()
        self.username = Entry(self.master, width=20, textvariable=self.user)
        self.password = Entry(self.master, width=20, show="*", textvariable=self.pw)
        self.username.grid(row=0, column=1)
        self.password.grid(row=1, column=1)
        self.label1 = Label(self.master, text="Username:").grid(row=0, column=0)
        self.label2 = Label(self.master, text="Password:").grid(row=1, column=0)
        self.next = Button(self.master, text="Sign In", command=self.login)
        self.quit = Button(self.master, text="Exit", command=self.destroy).grid(row=2,column=1)
        self.next.grid(row=2,column=0)
        self.username.focus()
            
    def login(self):
        if not DEBUG:
            good = True
            try:
                voice.login(self.user.get(),self.pw.get())
            except Exception:
                errorwin("Username/Password incorrect")
                good = False
            if good:
                del self.pw, self.user
                self.logged=True
                self.master.destroy()
        else:
            self.logged=True
            self.master.destroy()
               
            
    def destroy(self):
        self.master.destroy()  

def errorwin(message="Error!"):
    board = Toplevel()
    board.title("Error")
    error = Label(board, text=message, height=5).pack()
        
class mainwin:
    def __init__(self,master):
        self.root = Canvas(master)
        self.master=master
        master.title("Bulk SMS")
        self.dataset=[]
        self.filename = StringVar()
        self.filename.set("default.csv")
        self.textmessage = StringVar()
        
        self.filelabel = Label(master, text="Path:").grid(row=1,column=0)
        self.fileshow = Entry(master, width=20, textvariable=self.filename)
        self.fileshow.grid(row=1,column=1)
        self.filebrowse = Button(master, text="Browse", command=self.loadtemplate, width=10).grid (row=0,column=0)
        self.fileload = Button(master, text="Load File", command=self.loadcsv, width=10).grid(row=0,column=1)
        self.messagebox = Text(master, width=40, height=5)
        self.messagebox.grid(row=2,columnspan=2,column=0)
        self.sendbutton = Button(master, width=10, text="Send", command=self.sendmessage).grid(row=3,column=0)
        self.stopbutton = Button(master, width=10, text="Exit", command=self.logoff).grid(row=3,column=1)
        self.scroll = Scrollbar(master)
        self.scroll.grid(row=4,column=2,sticky='n'+'s')
        self.logbox = Text(master, state='disabled', width=40, height=LOGLENGTH, wrap='none')
        self.logbox.grid(row=4,column=0,columnspan=2)
        self.logbox.config(yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.logbox.yview)
        self.logwindow = loginwin()
        self.logwindow.master.mainloop()
        if self.logwindow.logged:
            self.master.mainloop()

            
    def logoff(self):
        if self.logwindow.logged and not DEBUG:
            voice.logout()
        self.master.destroy()
        
    def loadtemplate(self):
        filename = tkFileDialog.askopenfilename(filetypes = (("CSV", "*.csv"), ("All files", "*.*")))
        try:
            self.filename.set(filename)
        except:
            self.updatelog("Failed to read file\n'%s'"%filename)
            return
            
    def loadcsv(self):
        try:
            self.inp = open(self.filename.get(), 'r')
        except IOError:
            self.updatelog("Invalid File")
            return 0
        temp = self.inp.read()
        self.dataset = temp.replace(" ", "").replace("-", "").replace('\n','').replace('(','').replace(')','').split(',')
        
        self.updatelog("Loaded %s Phone Numbers"%len(self.dataset))
        self.inp.close()
        
    def sendmessage(self):
        self.textmessage = self.messagebox.get("1.0",END).replace('\n','')
        if not self.logwindow.logged:
            self.updatelog("Not Logged in")
        elif len(self.dataset)==0:
            self.updatelog("No phone numbers entered")
        elif len(self.textmessage)==0:
            self.updatelog("No text message entered")
        elif len(self.textmessage)>160:
            self.updatelog("Text message over 160 characters")
        else:
            good = True
            for i in range(len(self.dataset)):
                if len(self.dataset[i]) == 11 and self.dataset[i][0] == "1":
                    self.dataset[i] = self.dataset[i][1:]
                if len(self.dataset[i]) !=10:
                    self.updatelog("Phone number invalid Length: "+str(i))
                    good = False
                    break
            if good:
                self.updatelog("Sending Texts")
                for i in self.dataset:
                    self.updatelog(i)
                    if not DEBUG:
                        voice.send_sms(i, self.textmessage)
                self.updatelog(str(len(self.dataset))+" texts sent")        
            
                   
    def updatelog(self, msg):
        numlines = self.logbox.index('end - 1 line').split('.')[0]
        self.logbox['state'] = 'normal'
        if self.logbox.index('end-1c')!='1.0':
            self.logbox.insert('end', '\n')
        self.logbox.insert('end',msg)
        self.logbox['state'] = 'disabled'
        self.logbox.yview(END)
                
                
        
if __name__ == "__main__":
    voice = Voice()
    master = Tk()
    wind = mainwin(master)
