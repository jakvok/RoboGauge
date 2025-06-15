#!/usr/bin/python3

import Toollist, Gauge
import lxml.etree as et
import tkinter
from tkinter import ttk, messagebox, filedialog
import os, sys
from datetime import datetime

class SenderApp(tkinter.Tk):
    '''
    GUI app extracts machinig tool properties from XML file and sends the data into roboGauge
    '''

    def __init__(self, cfile='config.xml'):
        super().__init__()

        # get configuration from file
        try:
            xml = et.parse(cfile)  # parse configuration from config xml file
            for node in xml.iter():
                if node.tag == 'comport':
                    self.comport = node.text  # read comport for serial communication
                if node.tag == 'homedir':
                    self.homedir = node.text  # read home directory
                if node.tag == 'pitch':
                    self.pitch = node.text  # read gauge thread pitch
                if node.tag == 'stp_rev':
                    self.stp_rev = node.text    # read gauge motor step per revolution
                if node.tag == 'max_travel':
                    self.max_travel = node.text # read gauge max. travel
                if node.tag == 'offset_hsk63':
                    self.offset_hsk63 = node.text   # read Z-offset for HSK-63 holder
                if node.tag == 'offset_bt40':
                    self.offset_bt40 = node.text   # read Z-offset for BT-40 holder
                if node.tag == 'offset_captoc3':
                    self.offset_captoc3 = node.text   # read Z-offset for Capto C3 holder
        except:
            # create new config file if no one exists
            config = et.Element('configuration')
            port = et.SubElement(config, 'comport') # comport for serial communication
            port.text = self.comport = 'COM1'
            file = et.SubElement(config, 'homedir') # home directory
            file.text = self.homedir = os.getcwd()
            pitch = et.SubElement(config, 'pitch')
            pitch.text = self.pitch = '8.0'
            stp_rev = et.SubElement(config, 'stp_rev')
            stp_rev.text = self.stp_rev = '200.0'
            max_travel = et.SubElement(config, 'max_travel')
            max_travel.text = self.max_travel = '283.0'
            offset_hsk63 = et.SubElement(config, 'offset_hsk63')
            offset_hsk63.text = self.offset_hsk63 = '0.0'
            offset_bt40 = et.SubElement(config, 'offset_bt40')
            offset_bt40.text = self.offset_bt40 = '0.0'
            offset_captoc3 = et.SubElement(config, 'offset_captoc3')
            offset_captoc3.text = self.offset_captoc3 = '0.0'
            document = et.tostring(config, pretty_print=True, xml_declaration=True, encoding="utf-8")
            with open(cfile, 'wb') as f:
                f.write(document)

        # read holder list and assign holders offset
        try:
            with open('holders_hsk63.txt','r') as f:
                self.holders_hsk63 = f.read().splitlines()
        except:
            self.holders_hsk63 = []
        try:
            with open('holders_bt40.txt','r') as f:
                self.holders_bt40 = f.read().splitlines()
        except:
            self.holders_bt40 = []
        try:
            with open('holders_captoc3.txt', 'r') as f:
                self.holders_captoc3 = f.read().splitlines()
        except:
            self.holders_captoc3 = []


        # properties
        self.current_tools = Toollist.Toollist()       # list of tools get from XML file
        self.gauge = Gauge.Gauge(self.pitch, self.stp_rev, self.comport, self.max_travel)   # raise the device

        # GUI
        #-------------------------------

        # basic settings
        self.minsize(795,440) # dimmensions of main window
        self.resizable(True, True) # not resizable main window
        self.title('XML RoboGauge') # name of app

        # define look styles of some widgets
        style = ttk.Style()
        style.configure('INPUT.TEntry', font=('Sans', '15' ))
        style.configure('ALL.TLabel', font=('Sans', '12'))
        style.configure('OUT.TLabel', background='white', font=('Sans', '12'), width=30)
        style.configure('TOOL.TMenubutton', font=('Sans', '12'), width=39, background='#C3C3C3')
        style.configure('HOLDER.TMenubutton', font=('Sans', '12'), width=8)
        style.configure('ALL.TButton', font=('Sans', '12'))

        # init frames
        self.f00 = ttk.Frame(self)
        self.f0 = ttk.Labelframe(self, text='XML file')
        self.f1 = ttk.Labelframe(self, text='Tools')
        self.f2 = ttk.Labelframe(self, text='Offsets')
        self.f3 = ttk.Frame(self)

        # init tk variables
        self.inputfile = tkinter.StringVar(self)    # Path to XML file
        self.inputfile.set(self.homedir)
        self.sequence = tkinter.StringVar(self)     # sequence of tools from XML file
        self.TNumber = tkinter.IntVar(self)     # T-number of current tool
        self.TDuplo = tkinter.IntVar(self)      # Duplo number of current tool
        self.TLength = tkinter.DoubleVar(self)  # Z-length of current tool
        self.TDescription = tkinter.StringVar(self) # Description of current tool
        self.THolder = tkinter.StringVar(self)  # Holder type of current tool read from XML
        self.offset = tkinter.StringVar(self)   # Choosen current holder type
        self.offset_value = tkinter.DoubleVar(self) # Z-offset of choosen current holder
        self.Tpartname = tkinter.StringVar(self)    # Part name

        # init widgets

        # Part name displayed
        self.label_partname = ttk.Label(self.f00, textvariable=self.Tpartname, font = ('Sans', 14,'bold'))

        # Path to XML file
        self.entry_file = ttk.Entry(self.f0, textvariable=self.inputfile, font = ('Sans', 12), width=70)
        # Open XML file button
        self.button_file = ttk.Button(self.f0, text='OPEN', command=self._set_file, style='ALL.TButton')

        # list of extracted tools
        sequences = ['---']
        self.menu_seq = ttk.OptionMenu(self.f1,self.sequence, *sequences, style='TOOL.TMenubutton', command=self._set_values)
        self.sequence.set(sequences[0])

        # labels of tool properties
        self.label_TN = ttk.Label(self.f1, text='T:', style='ALL.TLabel')
        self.label_TD = ttk.Label(self.f1, text='Duplo:', style='ALL.TLabel')
        self.label_TL = ttk.Label(self.f1, text='Length Z:', style='ALL.TLabel')
        self.label_TDE = ttk.Label(self.f1, text='Descript.:', style='ALL.TLabel')
        self.label_TH = ttk.Label(self.f1, text='Holder:', style='ALL.TLabel')
        # tool properties values
        self.output_TN = ttk.Label(self.f1, textvariable=self.TNumber, style='OUT.TLabel')
        self.output_TD = ttk.Label(self.f1, textvariable=self.TDuplo, style='OUT.TLabel')
        self.output_TL = ttk.Label(self.f1, textvariable=self.TLength, style='OUT.TLabel')
        self.output_TDE = ttk.Label(self.f1, textvariable=self.TDescription, style='OUT.TLabel')
        self.output_TH = ttk.Label(self.f1, textvariable=self.THolder, style='OUT.TLabel')

        # List of available holder Z-offsets
        offsets = ['---','HSK-63A','BT-40','Capto C3','none']
        self.menu_offset = ttk.OptionMenu(self.f2,self.offset, *offsets, style='HOLDER.TMenubutton', command=self._set_offset )
        self.offset.set('---')
        # Offset label
        self.label_OFST = ttk.Label(self.f2, text='Offset  ', style='ALL.TLabel')
        # Z-offset value of current holder
        self.output_OFST = ttk.Label(self.f2, textvariable=self.offset_value, background='white', font=('Sans',12), width=8)

        # Serial communication button
        self.button_send = ttk.Button(self.f3, text='SEND', command=self._send_serial, style='ALL.TButton')
        # Exit app button
        self.button_exit = ttk.Button(self.f3, text='EXIT', command=lambda: sys.exit(0), style='ALL.TButton')

        #init geometry
        # f00 frame
        self.label_partname.grid(column=0, row=0)
        # f0 frame
        self.entry_file.grid(column=0, row=1, padx=(7, 7), pady=(2, 7), sticky='ew')
        self.button_file.grid(column=1, row=1, padx=(7, 7), pady=(2, 7))
        # f1 frame
        self.menu_seq.grid(column=2, row=3, padx=(7, 7), pady=(2, 7))
        self.label_TN.grid(column=0, row=3, sticky='E', padx=(9, 1))
        self.label_TD.grid(column=0, row=4, sticky='E', padx=(9, 1))
        self.label_TL.grid(column=0, row=5, sticky='E', padx=(9, 1))
        self.label_TDE.grid(column=0, row=6, sticky='E', padx=(9, 1))
        self.label_TH.grid(column=0, row=7, sticky='E', padx=(9, 1))
        self.output_TN.grid(column=1, row=3, pady=(7, 7))
        self.output_TD.grid(column=1, row=4, pady=(7, 7))
        self.output_TL.grid(column=1, row=5, pady=(7, 7))
        self.output_TDE.grid(column=1, row=6, pady=(7, 7))
        self.output_TH.grid(column=1, row=7, pady=(7, 7))
        # f2 frame
        self.menu_offset.grid(column=2, row=8)
        self.label_OFST.grid(column=0, row=8, padx=(7,1))
        self.output_OFST.grid(column=1, row=8, pady=(7, 7))
        # f3 frame
        self.button_send.grid(column=1, row=9, pady=(7, 7), padx=(275, 0))
        self.button_exit.grid(column=0, row=9, pady=(7, 7), padx=(0, 275))

        # frames geometry inside main window
        self.f00.grid(column=0, row=0, pady=(7, 7), padx=(7, 7))
        self.f0.grid(column=0, row=1, pady=(7, 7), padx=(7, 7))
        self.f1.grid(column=0, row=2, pady=(7, 7), padx=(7, 7), sticky='E')
        self.f2.grid(column=0, row=8, pady=(7, 7), padx=(7, 7), sticky='E')
        self.f3.grid(column=0, row=9, pady=(7, 7), padx=(7, 7), sticky='E')


    def _set_file(self):
        '''
        Find XML input file and fill Toollist object by list of tools
        Returns: None
        '''
        filetypes = (('XML files', '*.xml'), ('All files', '*.*'))  # define type of files for dialog window
        # raise tkinter file-selecting dialog window, returns filename path
        inputfile = filedialog.askopenfilename(title='Choose file to import', initialdir=self.homedir,
                                               filetypes=filetypes)

        if inputfile != '':
            # Set inputfile and extract partname from it
            self.inputfile.set(inputfile)
            self.Tpartname.set(os.path.basename(inputfile)[:-4])

            # get toollist from XML
            if self.current_tools.treat_xml(inputfile):
                self._log_text(' opened file ' + inputfile)
            else:
                self._log_text(' file opening error ' + inputfile)

            # fill Optionmenu by list of tools
            sequences = ['---']
            a = 1
            for n in self.current_tools.tools:
                sequences.append('ID{}  T{}  S{}  {}'.format( a, n['TNumber'], n['KeyDuploTool'], n['ToolDescription']))
                a=a+1
            self.menu_seq.set_menu(*sequences)
            self.sequence.set(sequences[0])
        else:
            self._log_text(' no XML file choosen ')


    def _set_values(self, value):
        '''
        Set current, selected tool properties into tkinter vars
        Args:
            value:<string> current value selected in Optionmenu of tools
        Returns:None
        '''

        # extract ID number from value
        id=''
        for x in value:
            if x.isdigit():
                id += x
            if x == ' ': break
        id = int(id) - 1

        # set current, selected tool properties from tool list
        self.TNumber.set(int(self.current_tools.tools[id]['TNumber']))
        self.TDuplo.set(int(self.current_tools.tools[id]['KeyDuploTool']))
        self.TLength.set(float(self.current_tools.tools[id]['Z']))
        self.TDescription.set(self.current_tools.tools[id]['ToolDescription'])
        self.THolder.set(self.current_tools.tools[id]['Holdernumber'])

        # set current Z-offset from current tool holder
        if self.THolder.get() in self.holders_hsk63:
            self.offset.set('HSK-63A')
            self.offset_value.set(self.offset_hsk63)
        elif self.THolder.get() in self.holders_bt40:
            self.offset.set('BT-40')
            self.offset_value.set(self.offset_bt40)
        elif self.THolder.get() in self.holders_captoc3:
            self.offset.set('Capto C3')
            self.offset_value.set(self.offset_captoc3)
        else:
            self.offset.set('none')
            self.offset_value.set(0.0)


    def _set_offset(self, value):
        '''
        Set holder z-offset value according to selected holder
        Args:
            value: <string> selected value from holder Optionmenu
        Returns: None

        '''
        if value == 'HSK-63A':
            self.offset_value.set(self.offset_hsk63)
        elif value == 'BT-40':
            self.offset_value.set(self.offset_bt40)
        elif value == 'Capto C3':
            self.offset_value.set(self.offset_captoc3)
        else:
            self.offset_value.set(0.0)

    def _send_serial(self):
        '''
        Send final Z value to Robogauge via serial line
        Returns: None
        '''
        if self.offset_value.get() <= 0.0:
            messagebox.showwarning(title='WARNING!', message='Holder has zero length!')
            self._log_text(' Holder has zero length!')
        elif self.TLength.get() <= 0.0:
            messagebox.showwarning(title='WARNING!', message='Tool has zero length!')
            self._log_text(' Tool has zero length!')
        else:
            if self.gauge.send(self.offset_value.get()-self.TLength.get()):
                self._log_text(' Z' + str(self.TLength.get()) + ' offset' + str(self.offset_value.get()) + ' sent')
            else:
                self._log_text(' communication error')

    def _log_text(self, text):
        '''
        Logs messages into file
        Args:
            text: log message
        Returns: None
        '''
        dt_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('bazmek1.log', 'a', encoding='utf-8') as f:
            #f.write(dt_string + self.Tpartname.get() + ' T' + str(self.TNumber.get()) + ' S' + str(self.TDuplo.get()) + str(text) + '\n')
            f.write('{}  {} T{} S{} {}\n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.Tpartname.get(), self.TNumber.get(), self.TDuplo.get(), text))



if __name__ == '__main__':
    app = SenderApp()
    app.mainloop()