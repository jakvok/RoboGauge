#!/usr/bin/python3

from lxml import etree
from tkinter import messagebox

class Toollist:
    '''
    Class repr list of tools contained in Haimer XML file with
    all relevant properties.
    
    object variable <list>"tools" with <dict>"tool" elements
            with keys: 
            "TNumber"
            "KeyDuploTool"
            "ToolDescription"
            "Holdernumber"
            "Z"
    '''
    
    
    def __init__(self) -> None:
        self.tools = []   # list of tools from xml file



    def treat_xml(self, filename):
        '''
        -read XML file and extract all tools and their properties
        -save it into object variable "tools"
        '''
        try:
            with open(filename,'r',encoding='utf-8') as f:
                xml = f.read()
        except FileNotFoundError:
            print('XML File not found.')

        self.tools = [] # delete tool list if new XML file read

        try:
            root = etree.fromstring(xml)
            for orders in root.getchildren():
                for order in orders.getchildren():
                    tool = {}    # tool with its properties
                    for tuul in order.getchildren():
                        for n in ["TNumber","KeyDuploTool","ToolDescription","Holdernumber"]:
                            if tuul.tag == n:
                                tool[n] = tuul.text
                        if tuul.tag == "STAGE":
                            for stage in tuul.getchildren():
                                if stage.tag == "Z":
                                    tool["Z"] = stage.text
                    if tool != {}:
                        self.tools.append(tool)
            return True
        except:
            messagebox.showwarning(title='WARNING!', message='Unsupported XML format.')
            return False
    



if __name__ == '__main__':
    pass

