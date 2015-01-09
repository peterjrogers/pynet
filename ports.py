from tools import Tools
import os

class Ports(Tools):
    def __init__(self, verbose=0):
        Tools.__init__(self)
        """
        Well known port search tool
        
        downloaded port list from
        http://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv
        
        format of csv file
        Service Name,Port Number,Transport Protocol,Description,Assignee,Contact,Registration Date,Modification Date,Reference,Service Code,Known Unauthorized Uses,Assignment Notes
        ftp-data,20,tcp,File Transfer [Default Data],[Jon_Postel],[Jon_Postel],,,,,,
        ftp-data,20,udp,File Transfer [Default Data],[Jon_Postel],[Jon_Postel],,,,,,
        
        format of dictionary
        [portnum_protocol]['name'] = name
        [portnum_protocol]['description'] = description
        
        Tested with Python ver 2.7.2 on Win7 & Win XP
        (c) 2012 - 2014 Intelligent Planet Ltd
        
        """
        
        self.verbose = verbose
        self.port_dict = {}
        self.path = os.getcwd() + '\\'
        self.load_file = self.path + 'ports.csv'
        self.load()
        
    def load(self):
        file = open(self.load_file, 'rU')
        for row in file:
            if row:
                try:
                    key = len(self.port_dict) + 1
                    raw = row.split(',')
                    self.port_dict[key] = {}
                    self.port_dict[key]['name'] = raw[0].lower()
                    self.port_dict[key]['port'] = int(raw[1])
                    self.port_dict[key]['protocol'] = raw[2].lower()
                    self.port_dict[key]['description'] = raw[3].lower()
                except: 
                    if self.verbose > 0: print 'error', row
                    try: del self.port_dict[key]
                    except: pass
                    
                    
    def test(self):
        for num in range(0, 1000): print self.find_port(num)
        
        
    def display_record(self, port, protocol, name, description):
        print port, self.space(port, 7), protocol, self.space(protocol), name, self.space(name, 20), description
                
                
    def find_port(self, search, proto='tcp'):
        try:             
            key_list = self.port_dict.keys()
            for key in key_list:
                port = self.port_dict[key]['port']
                protocol = self.port_dict[key]['protocol']
                name = self.port_dict[key]['name']
                description =  self.port_dict[key]['description']

                #search on port number
                try:
                    if int(search) == port and protocol == proto.lower(): 
                        self.display_record(port, protocol, name, description)
                        return #name.upper(), description
                except: pass
                
                #search on port name
                if name == search and protocol == proto.lower(): 
                    self.display_record(port, protocol, name, description)
                    return #port, description
                
                #search on like match of description
                if search in description: self.display_record(port, protocol, name, description)
                
                #search on like match of name
                elif search in name: self.display_record(port, protocol, name, description)
        
        except: pass
                        
                            
