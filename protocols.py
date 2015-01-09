from tools import Tools
import os

class Protocols(Tools):
    def __init__(self, verbose=0):
        Tools.__init__(self)
        """
        Assigned Internet Protocol Numbers search tool
        
        downloaded port list from
        http://www.iana.org/assignments/protocol-numbers/protocol-numbers-1.csv
        
        format of csv file
        Decimal,Keyword,Protocol,Reference
        0,HOPOPT,IPv6 Hop-by-Hop Option,[RFC2460]
        1,ICMP,Internet Control Message,[RFC792]
        
        format of dictionary
        [Protocol_num]['name'] = name
        [Protocol_num]['description'] = description
        
        Tested with Python ver 2.7.2 on Win7 & Win XP
        (c) 2012 - 2014 Intelligent Planet Ltd
        """
        
        self.verbose = verbose
        self.protocol_dict = {}
        
        self.path = os.getcwd() + '\\'
        self.load_file = self.path + 'protocols.csv'
        self.load()
        
    def test(self): 
        for num in range(0, 256): print self.find_protocol(num)
        
        
    def load(self):
        file = open(self.load_file, 'rU')
        for row in file:
            if row:
                try:
                    raw = row.split(',')
                    key = int(raw[0])    #key is an integer to check the row is valid
                    self.protocol_dict[key] = {}
                    self.protocol_dict[key]['name'] = raw[1]
                    self.protocol_dict[key]['description'] = raw[2]
                except: 
                    if self.verbose > 0: print 'error', row
                
                
    def find_protocol(self, protocol_num):
        try: 
            key = int(protocol_num)
            name = self.protocol_dict[key]['name'].upper().rstrip()
            desc = self.protocol_dict[key]['description'].rstrip()
            return name, desc
        
        except: return 'fail', protocol_num
                        
                            
