from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import time, os, datetime
from subprocess import Popen,PIPE
import serial, threading
import configparser
import serial.tools.list_ports as comports
from tkinter import messagebox
#Application start
class term_app(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.protocol('WM_DELETE_WINDOW', self.term_app_close)
        self.logging = False
        self.ser_open = False
        self.config_init()
        self.log_init()
        self.widget()
        return
    #Logging initialisation
    def log_init(self):
        self.batlog_file = []
        self.snbat_dir, self.cm4bat_dir, self.itmbat_dir = '', '', ''
    #Defining window size
    def window_size(self):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.ww = int(sw / 2)
        self.wh = int(sh / 1.2)
        self.wx = sw - self.ww - 150
        self.wy = 5
        self.swx = self.wx + 20
        self.swy = self.wy + 50
    #Do nothing function for not functioned menus and button
    def donothing(self):
        print('do nothing')
    def print(self):
        '''printers=win32print.ge
        print_window=Toplevel(self)
        print_window.geometry('300x250+%s+%s' % (self.swx, self.swy))
        Label(print_window,text='Select printer').grid(row=1,column=1)
        printer_sel=ttk.Combobox(print_window,values=printers)
        printer_sel.grid(row=1,column=2)'''
    #MAIN window widgets
    def widget(self):
        self.window_size()
        self.title('75F TERM(RAVI)')
        self.geometry('%sx%s+%s+%s' % (self.ww, self.wh, self.wx, self.wy))
        self.resizable(True, True)
        self.lift()
        self.menubar = Menu(self)
        # File menu options
        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label='New', command=lambda :term_app().mainloop())
        '''filemenu.add_command(label='Open', command=self.donothing)'''
        # Adding logmenu to file menu and in logmenu creating submenu start and stop
        logmenu = Menu(filemenu, tearoff=0)
        filemenu.add_cascade(label='Log', menu=logmenu)
        logmenu.add_command(label='Start Log', command=self.start_log)
        logmenu.add_command(label="Stop log", command=self.stop_log)
        '''filemenu.add_command(label='Save as', command=self.donothing)'''
        filemenu.add_command(label='Disconnect', command=lambda :[self.ser_close(),self.title('75F TERM(RAVI) [disconnected]')])
        '''printmenu = Menu(filemenu , tearoff=0)
        # creating submenu for print menu
        filemenu.add_cascade(label='Print', menu=printmenu)
        printmenu.add_command(label='Print', command=self.print)
        printmenu.add_command(label='Print preview', command=self.donothing)'''
        filemenu.add_command(label='Quit', command=self.quit)
        self.menubar.add_cascade(label='File', menu=filemenu)

        # Edit menu options
        editmenu = Menu(self.menubar, tearoff=0)
        editmenu.add_command(label='Cut', command=lambda :self.ser_text_box.event_generate('<<Cut>>'))
        editmenu.add_command(label='Copy', command=lambda :self.ser_text_box.event_generate('<<Copy>>'))
        editmenu.add_command(label='Paste', command=lambda :self.ser_text_box.event_generate('<<Paste>>'))
        self.menubar.add_cascade(label='Edit', menu=editmenu)

        # Setup menu options
        self.menubar.add_command(label='Serial Port', command=self.serial_port)
        # Program Menu
        self.programmenu = Menu(self.menubar, tearoff=0)
        self.programmenu.add_command(label='Program', command=self.program_GUI)
        self.programmenu.add_command(label='select flashtool directory', command=self.flashtool_dir)
        self.menubar.add_cascade(label='Program', menu=self.programmenu)
        # About menu options
        self.menubar.add_command(label='About', command=self.about)
        # configering self.menubar as mainmenu
        self.config(menu=self.menubar)
        # Textbox to print TX RX data
        vscrollbar = Scrollbar(self)
        self.ser_text_box = Text(self, width=200, height=40, yscrollcommand=vscrollbar.set, wrap='word',state=DISABLED)
        vscrollbar.pack(side=RIGHT, fill=BOTH)
        self.ser_text_box.pack(side=RIGHT, fill=Y)
        vscrollbar.config(command=self.ser_text_box.yview)

    # Displaying about tool in about menu
    def about(self):
        messagebox.askokcancel('About', '''
        ver. 1.0
1. This is serial tereminal tool support for all serial devices
2. It is having programming feature for only 75F smart devices
    Devices: Smartnode, CM4 and ITM

Developed by:
    RAVIKIRANA B,
    Testing Engineer,75F India''')

    # Opening serial port configeration window
    def serial_port(self):
        self.menubar.entryconfig('Serial Port', state='disabled')
        self.serial_port_window = Toplevel(self)
        self.serial_port_window.title('serial port configeration')
        self.serial_port_window.geometry('250x250+%s+%s' % (self.swx, self.swy))
        self.serial_port_window.resizable(False, False)
        self.serial_port_window.lift(self)
        self.serial_port_window.config(bg='darkorange')
        #Checking binding X to enable 'Serial port'
        self.serial_port_window.protocol("WM_DELETE_WINDOW",
                                     lambda :[self.menubar.entryconfig('Serial Port', state='normal'),self.serial_port_window.destroy()])
        # com port selection
        com_port_label = Label(self.serial_port_window, text='COM port', bg='darkorange')
        com_port_label.place(x=10, y=5)
        self.com_ports_available = comports.comports()
        self.comport_select = ttk.Combobox(self.serial_port_window, values=self.com_ports_available,
                                           width=10)
        if self.com_ports_available:
            self.comport_select.current(0)
        self.comport_select.place(x=80, y=5)
        # Baudrate selection
        baudrate_label = Label(self.serial_port_window, text='Baudrate', bg='darkorange')
        baudrate_label.place(x=10, y=35)
        self.baudrate_select = ttk.Combobox(self.serial_port_window, values=serial.Serial.BAUDRATES,
                                            width=10)
        self.baudrate_select.current(16)
        self.baudrate_select.place(x=80, y=35)
        # selecting data size
        datasize_label = Label(self.serial_port_window, text='Data size', bg='darkorange')
        datasize_label.place(x=10, y=65)
        self.datasize_select = ttk.Combobox(self.serial_port_window, values=serial.Serial.BYTESIZES,
                                            width=10)
        self.datasize_select.current(3)
        self.datasize_select.place(x=80, y=65)

        # parity selection
        parity_label = Label(self.serial_port_window, text='Parity', bg='darkorange')
        parity_label.place(x=10, y=95)
        self.parity_select = ttk.Combobox(self.serial_port_window, values=serial.Serial.PARITIES, width=10)
        self.parity_select.current(0)
        self.parity_select.place(x=80, y=95)

        # Handshake selection
        flow_control_label = Label(self.serial_port_window, text='Flow control', bg='darkorange')
        flow_control_label.place(x=10, y=125)
        std_flow_control = 'OFF', 'RTS/CTS', 'Xon/Xoff'
        self.flow_control_select = ttk.Combobox(self.serial_port_window, values=std_flow_control,
                                                width=10)
        self.flow_control_select.current(0)
        self.flow_control_select.place(x=80, y=125)
        # Stopbit selection
        stopbits_label = Label(self.serial_port_window, text='Stop bit', bg='darkorange')
        stopbits_label.place(x=10, y=155)
        self.stobit_select = ttk.Combobox(self.serial_port_window, values=serial.Serial.STOPBITS, width=10)
        self.stobit_select.current(0)
        self.stobit_select.place(x=80, y=155)
        # OK button to setup COM port
        open_port_button = Button(self.serial_port_window, text='OK', command=lambda :[self.open_port(),self.serial_port_window.destroy()], bg='olive')
        open_port_button.place(x=30, y=185)
        open_port_button = Button(self.serial_port_window, text='CANCEL', bg='olive', command=lambda :[self.menubar.entryconfig('Serial Port', state='normal'),self.serial_port_window.destroy()])
        open_port_button.place(x=75, y=185)
        return

    # Opening port
    def open_port(self):
        try:
            self.menubar.entryconfig('Serial Port', state='normal')
            # Opening selected port
            if self.com_ports_available:
                com_port_selected = self.comport_select.get()
                print(com_port_selected)
                com_port_selected = re.match(r"(^\w*\d)",com_port_selected,re.I)
                com_port = com_port_selected.group(0)
                # Opening selected port
                self.ser = serial.Serial(com_port,timeout=0)
                self.ser_open = True
                self.title('75F TERM (RAVI) [%s]' % (com_port))
                self.port_config()
                # To read serial data
                self.ser_read()
                # If any data entered in Text widget, that data is sending in serial port
                self.ser_text_box.bind('<Key>', lambda ser_textbox_event: self.ser_write(ser_textbox_event))
                self.serial_port_window.destroy()
            else:
                messagebox.showinfo('COM port error', 'COM port is not available')
        # Handling serial liabrary errors
        except serial.SerialException:
            try:
                if self.ser.isOpen():
                    self.ser.close()
                    self.open_port()
            except Exception:
                messagebox.showinfo('COM port error', 'cannot open %s.Access is denied' % (com_port))
                self.title('75F TERM(RAVI) [disconnected]')

    # Closing serial port if opened
    def ser_close(self):
        if self.ser_open is True:
            self.ser.close()
            self.ser_open = False
        else:
            messagebox.showinfo('Port error', 'Port not opened')

    # writing data to serial if any data entered in input textbox
    def ser_write(self, ser_textbox_event):
        datatosend = ser_textbox_event.char
        if self.ser.isOpen():
            self.ser.write(datatosend.encode('utf-8','ignore'))
        return

    # Serial port read
    def ser_read(self):
        if self.ser_open is True:
            while self.ser.inWaiting():
                received_data = self.ser.readline().decode('utf-8','ignore')
                data=re.sub(r'[^\w\s\d\n _ = . : ? / ! * < > -? ]','-',received_data,re.UNICODE)
                self.ser_text_box.config(state=NORMAL)
                self.ser_text_box.insert(END, data)
                self.ser_text_box.config(state=DISABLED)
                if self.logging is True:
                    self.log(data)
                self.ser_text_box.yview_pickplace('end')
        if self.ser.isOpen():
            self.after(100, self.ser_read)
        return

    # Configering serial port parameters
    def port_config(self):
        if self.ser.isOpen():
            # Baudrate selection
            self.ser.baudrate = self.baudrate_select.get()
            # Datasize selection
            self.ser.bytesize = int(self.datasize_select.get())
            # Parity selection
            self.ser.parity = self.parity_select.get()
            # Stopbits selection
            self.ser.stopbits = int(self.stobit_select.get())
            print(self.ser.get_settings())
        return

    # Logging serial data into text file with date & time
    # logging file default name format is "log_date_time.txt"
    def start_log(self):
        if self.logging is False:
            log_filename = 'log_' + time.strftime('%Y%m%d_%H%M%S') + '.txt'
            self.logdir = filedialog.asksaveasfilename(initialfile=log_filename, title='select file',
                                                       filetypes=(('.txt file', '*.txt'), ('all files', '*.*')))
            if self.logdir:
                self.logging = True
        else:
            messagebox.showinfo('Logging info', 'Already logging')
        return

    # Stop logging if logging started and closing logging file
    def log(self,data):
        log_file=open(self.logdir,'a+')
        timestamp=str(time.strftime("[%m/%d/%Y %H:%M:%S]\t",time.localtime()))
        log_file.write('%s: %s\t'%(timestamp,data))
        #print('%s: %s\t'%(timestamp,data))
        log_file.close()
    def stop_log(self):
        if self.logging == True:
            self.logging = False
            self.logfile.close()
        else:
            messagebox.showinfo('Log error', 'Logging not started')
        return

    # Capturing FLASHTOOL directory and creating file "config_files"
    def flashtool_dir(self):
        tool_dir = filedialog.askdirectory()
        print(tool_dir)
        if tool_dir:
            self.config_ini.set('FLASHTOOL INFORMATION', 'FLASTOOL DIR', tool_dir)
            self.configini = open('./config_files/configeration.ini', 'w')
            self.config_ini.write(self.configini)
            self.configini.close()
            print('tool director is selected')
            if 'config_files' in os.listdir(tool_dir):
                None
                #print(os.listdir(tool_dir))
            else:
                os.mkdir(tool_dir + '/config_files')
        return

    # Setting up intial programming configeration
    def config_init(self):
        self.config_ini = configparser.ConfigParser()
        self.config_ini.read('./config_files/configeration.ini')
        if 'config_files' in os.listdir('.'):
            if 'configeration.ini' in os.listdir('./config_files/'):
                if self.config_ini.has_section('FLASHTOOL INFORMATION'):
                    None
                else:
                    self.config_ini.add_section('FLASHTOOL INFORMATION')
                    self.config_ini.set('FLASHTOOL INFORMATION', 'FLASTOOL DIR', '')
                if self.config_ini.has_section('APP DETAILS'):
                    None
                else:
                    # Adding all configeration in .ini file
                    self.config_ini.add_section('APP DETAILS')
                    self.config_ini.set('APP DETAILS', 'TOOL SN', '')
                    self.config_ini.set('APP DETAILS', 'Device name', '')
                    self.config_ini.set('APP DETAILS', 'application file', '')
                    self.config_ini.set('APP DETAILS', 'Backup file', '')
                    self.config_ini.set('APP DETAILS', 'Backup ver', '')
                    self.config_ini.set('APP DETAILS', 'Bootloader file', '')
                    self.config_ini.set('APP DETAILS', 'application ver', '')
                    self.config_ini.set('APP DETAILS', 'Bootloader ver', '')
                    self.config_ini.set('APP DETAILS', 'Bootloader', '')
                    configini = open('./config_files/configeration.ini', 'w')
                    self.config_ini.write(configini)
                    configini.close()
            else:
                configini = open('./config_files/configeration.ini', 'w')
                self.config_ini.write(configini)
                configini.close()
                self.config_init()
        else:
            os.mkdir('./config_files')
            self.config_init()

    # Creating programming window and it' elements
    def program_GUI(self):
        #Disbling program menu option to avoid multi program window
        self.programmenu.entryconfig('Program', state='disabled')
        #opening programming window
        self.program_window=Toplevel(self)
        self.program_window.title('Programming...')
        self.program_window.geometry('500x400+%s+%s' % (self.swx, self.swy))
        self.program_window.resizable(False, False)
        self.program_window.lift(self)
        self.program_window.config(bg='orange')
        #Checking binding X to enable Program menu option
        self.program_window.protocol("WM_DELETE_WINDOW", lambda :[self.programmenu.entryconfig('Program', state='normal'),self.program_window.destroy()])
        self.program_window_widget()
    def program_window_widget(self):
        # Reading configeration file
        self.config_ini.read('./config_files/configeration.ini')
        #variable declaration for Entry or Text entry
        self.app_ver, self.backup_ver, self.bootloader_ver=StringVar(), StringVar(), StringVar()
        #Programming tool information
        Label(self.program_window,text='TOOL',font='arial 10',bg='orange').place(x=20,y=10)
        self.tool=Text(self.program_window,height=1,width=15)
        self.tool.insert(0.0,self.config_ini.get('APP DETAILS', 'TOOL SN'))
        self.tool.place(x=140,y=10)
        #Select devices
        Label(self.program_window, text='Select devices', font='arial 10', bg='orange').place(x=20, y=40)
        devices = 'smartnode', 'cm4', 'itm'
        self.selected_device=ttk.Combobox(self.program_window,width=17,values=devices)
        self.selected_device.set(self.config_ini.get('APP DETAILS', 'Device name'))
        if self.selected_device.get() == '':
            self.selected_device.current(0)
        self.selected_device.place(x=140,y=40)
        #App ver.
        Label(self.program_window, text='App ver.', font='arial 10', bg='orange').place(x=20, y=70)
        app_ver=Entry(self.program_window,width=20,textvariable=self.app_ver)
        app_ver.insert(END,self.config_ini.get('APP DETAILS', 'application ver'))
        app_ver.place(x=140,y=70)
        #App hex file
        Label(self.program_window, text='App hex file', font='arial 10', bg='orange').place(x=20, y=100)
        app_hexfile=Text(self.program_window,width=30,height=1)
        app_hexfile.insert(0.0,self.config_ini.get('APP DETAILS', 'application file'))
        app_hexfile.place(x=140,y=100)
        Button(self.program_window,text='/',bg='darkorange',width=3,command=lambda :self.askfile('application file', '*.hex' )).place(x=390,y=100)
        #Backup ver.
        Label(self.program_window, text='Backup ver.', font='arial 10', bg='orange').place(x=20, y=130)
        backup_ver = Entry(self.program_window, width=20,textvariable=self.backup_ver)
        backup_ver.insert(END, self.config_ini.get('APP DETAILS', 'Backup ver'))
        backup_ver.place(x=140, y=130)
        #Checking Backup needed or not
        self.backupvarvar = BooleanVar()
        Checkbutton(self.program_window, variable=self.backupvarvar, bg='orange').place(x=250, y=130)
        #Backup hex file
        Label(self.program_window, text='Backup hex file', font='arial 10', bg='orange').place(x=20, y=170)
        backup_hexfile = Text(self.program_window, width=30,height=1)
        backup_hexfile.insert(0.0,self.config_ini.get('APP DETAILS', 'Backup file'))
        backup_hexfile.place(x=140, y=170)
        Button(self.program_window, text='/', width=3, bg='darkorange',command=lambda :self.askfile('backup file','*.hex')).place(x=390, y=170)
        #Bootloader ver.
        Label(self.program_window, text='Bootloader ver.', font='arial 10', bg='orange').place(x=20, y=200)
        bootloader_ver = Entry(self.program_window, width=20,textvariable=self.bootloader_ver)
        bootloader_ver.insert(END,self.config_ini.get('APP DETAILS', 'Bootloader ver'))
        bootloader_ver.place(x=140, y=200)
        #Checking bootloader needed or not
        self.bootloadervar=StringVar(value=self.config_ini.get('APP DETAILS', 'Bootloader'))
        Checkbutton(self.program_window,variable=self.bootloadervar,onvalue='True',offvalue='False',bg='orange').place(x=250,y=200)
        #Bootloader hex file
        Label(self.program_window, text='Bootloader hex file', font='arial 10', bg='orange').place(x=20, y=230)
        bootloader_hexfile = Text(self.program_window, width=30, height=1)
        bootloader_hexfile.insert(0.0,self.config_ini.get('APP DETAILS', 'Bootloader file'))
        bootloader_hexfile.place(x=140, y=230)
        Button(self.program_window, text='/', width=3, bg='darkorange',command=lambda :self.askfile('bootloader file','*.hex')).place(x=390, y=230)
        #Program button
        self.program_button=Button(self.program_window, text='PROGRAM', font='arial 10', bg='darkorange',command=self.program)
        self.program_button.place(x=150, y=270)
        #Programming status Textbox
        self.pgm_status_out=Text(self.program_window, font='arial 10',height=4,width=63,wrap=WORD)
        self.pgm_status_out.place(x=20, y=310)
        vscrollbar = Scrollbar(self.program_window,command=self.pgm_status_out.yview)
        vscrollbar.place(x=465,y=310,height=68)
        self.pgm_status_out['yscrollcommand']=vscrollbar.set
        self.program_config()
        self.program_window.mainloop()
    def program(self):
        self.pgm_thread=threading.Thread(target=self.start_program)
        self.pgm_thread.start()
        self.flash_error = False
        self.program_button.config(state=DISABLED,text='programming...')
        self.pgm_status_out.config(fg='green')
        self.pgm_status_out.delete(0.0,END)
        self.boot=True
        self.pgm_killed=False
    def program_config(self):
        try:
            thread = threading.Timer(1, self.program_config)
            # Saving all data into configeration file "configeration.ini"
            self.config_ini.set('APP DETAILS', 'TOOL SN', self.tool.get(0.0, END))
            self.config_ini.set('APP DETAILS', 'Device name', self.selected_device.get())
            self.config_ini.set('APP DETAILS', 'application ver', self.app_ver.get())
            self.config_ini.set('APP DETAILS', 'Bootloader ver', self.bootloader_ver.get())
            self.config_ini.set('APP DETAILS', 'Backup ver', self.backup_ver.get())
            self.config_ini.set('APP DETAILS', 'Bootloader', str(self.bootloadervar.get()))
            configini = open('./config_files/configeration.ini', 'w+')
            self.config_ini.write(configini)
            configini.close()
            self.program_window.update()
            thread.start()
        except Exception:
            thread.cancel()
    #Capturing hex filenames
    def askfile(self, name ,type):
        file=filedialog.askopenfilename(filetypes=(('%s files'%type,type),))
        if file:
            self.config_ini.set('APP DETAILS',name,file)
            self.configini = open('./config_files/configeration.ini', 'w')
            self.config_ini.write(self.configini)
            self.configini.close()
        self.program_window.lift(self)
        self.program_window_widget()
    # Opening command prompt in flashtool directory and sending flashing commands
    def start_program(self):
        try:
            print('programming')
            device=self.selected_device.get()
            tool_dir = self.config_ini.get('FLASHTOOL INFORMATION', 'FLASTOOL DIR')
            self.set_ini = configparser.ConfigParser()
            ini_readpath = tool_dir + '/%s.ini' % device
            self.set_ini.read(ini_readpath)
            print(ini_readpath)
            self.set_ini.set('ToolInfo', 'Serial', self.config_ini.get('APP DETAILS', 'TOOL SN'))
            self.set_ini.set('FirmwareInfo', 'BootloaderFirmwareVersion',self.bootloader_ver.get())
            self.set_ini.set('FirmwareInfo', 'Bootloader', self.config_ini.get('APP DETAILS', 'bootloader file'))
            # cmd1 = 'flashtool.exe -f "' + tool_dir + '/config_files/%s.ini" -c flashmanufacture' % device
            cmd1 = f"flashtool.exe -f ./config_files/{device}.ini -c flashmanufacture"
            cmd2= f'flashtool.exe -c flashapp -f ./config_files/{device}.ini'
            # cmd1='flashtool.exe -f "E:/Ravikiran/FLASHTOOL 1/flashtool-v2.4.0/config_files/smartnode.ini" -c flashmanufacture'
            # Checking backup flash ver. is enetered or not
            # If back up ver. is there then flashing backup ver. and erasing flashing
            if self.backupvarvar.get():
                print('entered into backup version')
                # Flashing backup ver.
                self.pgm_status_out.insert(END,'Started flashing Backup ver...\n')
                self.set_ini.set('FirmwareInfo', 'ApplicationFirmwareVersion', self.backup_ver.get())
                self.set_ini.set('FirmwareInfo', 'ApplicationImage', self.config_ini.get('APP DETAILS', 'Backup file'))
                open_ini = open(tool_dir + '/config_files/%s.ini' % device, 'w')
                self.set_ini.write(open_ini)
                open_ini.close()
                if self.bootloadervar.get() == 'True':
                    cmd = cmd1
                    progress_time =170
                else:
                    cmd = cmd2
                    progress_time = 100
                print(cmd)
                self.pgmcmd = Popen('cmd /c' + cmd, cwd=tool_dir,stdout=PIPE)
                self.command_prompt('Backup ver. flashing done\n',progress_time)
                time.sleep(2)
                self.boot=False
                # Erasing backup ver.
                if self.pgm_killed is False:
                    self.pgm_status_out.insert(END,'Started erasing...\n')
                    cmd3 = 'flashtool.exe -c erasebackup -f ' + tool_dir + '/config_files/%s.ini' % device
                    self.pgmcmd =Popen('cmd /c' + cmd3, cwd=tool_dir, stdout=PIPE)
                    self.command_prompt('Erasing done.\n',15)
                    time.sleep(13)
            # Flashing application ver
            if self.pgm_killed is False:
                self.pgm_status_out.insert(END,'Flashing application ver...\n')
                self.set_ini.set('FirmwareInfo', 'ApplicationFirmwareVersion',
                                 self.config_ini.get('APP DETAILS', 'application ver'))
                self.set_ini.set('FirmwareInfo', 'ApplicationImage', self.config_ini.get('APP DETAILS', 'application file'))
                open_ini = open(tool_dir + '/config_files/%s.ini' % device, 'w')
                self.set_ini.write(open_ini)
                open_ini.close()
                if (self.bootloadervar.get() == 'True' ) and (self.bootloadervar.get()):
                    cmd=cmd1
                    progress_time = 170
                else:
                    cmd=cmd2
                    progress_time = 100
                print(cmd)
                self.pgmcmd = Popen('cmd /c' + cmd, cwd=tool_dir, stdout=PIPE,shell=True)
                self.command_prompt('Flashing app ver done.\n',progress_time)
                self.program_button.config(text='PROGRAM', state=NORMAL)
        except Exception as e:
            print(e)
            if re.search(r'No section',str(e),re.I):
                messagebox.showinfo('Info','Please select FLASHTOOL directory')
                self.program_window.lift()
                self.program_button.config(text='PROGRAM', state=NORMAL)
            else:
                print(e)
        return
    def command_prompt(self,status,maxvalue):
        #self.pgmcmd.poll()
        self.progress=ttk.Progressbar(self.program_window,orient='horizontal',maximum=maxvalue,length=200)
        self.progress.place(x=260,y=275)
        self.progress.start(interval=1000)
        # Reading command prompt output and displaying the errors
        while self.pgmcmd.poll() is None:
            out=self.pgmcmd.stdout.readline()
            self.pgmcmd.stdout.flush()
            print(str(out))
            errors=['No device detected','Could not find tool','No Firmware Version Embedded In Image','Failed to Locate',\
                    'Unexpected Chip Identifier','Could not establish connection to device','Invalid Config Item ',\
                    'Unrecognized or ambiguous command','Firmware Version Mismatch','Could not write ARM memory','ERROR']
            error_dict={'No device detected':'Pls check connection!!','Could not find tool':'Pls check programmer connected or not and serial number of programmer!!',\
                        'No Firmware Version Embedded In Image':'Pls select proper hex files!!','Failed to Locate':'Check hex files inserted or not!!',\
                    'Unexpected Chip Identifier':'Pls select proper hex files!!','Could not establish connection to device':'Please check connection!!','Invalid Config Item ':'Check FW version!!',\
                    'Unrecognized or ambiguous command':'check programmer serial number!!','Firmware Version Mismatch':'Insert proper version hex file!!','Could not write ARM memory':'!!','ERROR':'!!'}
            for error in errors:
                error_search = re.search(error, str(out), re.I)
                if error_search:
                    self.pgm_status_out.config(fg='HotPink')
                    self.pgm_status_out.insert(END,'Error: '+error_search.group()+' -? '+error_dict[error_search.group()]+'\n')
                    self.pgm_status_out.yview_pickplace('end')
                    self.flash_error=True
            if self.flash_error:
                self.progress.destroy()
                self.program_button.config(text='PROGRAM', state=NORMAL)
                self.pgmcmd.kill()
                self.pgm_killed=True
                return
                self.pgm_thread.join()
        time.sleep(2)
        self.progress.destroy()
        if self.flash_error is False:
            self.pgm_status_out.insert(END,status+'\n')
        return
    def term_app_close(self):
        if messagebox.askokcancel('Quit','Are you really want to exit'):
            self.destroy()
