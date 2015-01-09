import re, os
from tools import Tools

class Mac(Tools):
    def __init__(self):
        Tools.__init__(self)
        
        """
        MAC lookup to identify the vendor from the OUI of the mac address
        
        Usage example:
        >>> x = mac.Mac()
        >>> x.id_mac('0000.0c07.ac03')
        ('Cisco', 'CISCO SYSTEMS')
        
        Tested with Python ver 2.7.2 on Win7 & Win XP
        (c) 2012 - 2014 Intelligent Planet Ltd
        """
        
        if '\\' in os.getcwd():  self.path = os.getcwd() + '\\'
        else: self.path = os.getcwd() + '/'
        
        self.mac_file = self.path + 'mac'    
        self.mac_file_url = 'http://anonsvn.wireshark.org/wireshark/trunk/manuf'
        self.oui_list = []
        
        try: self.load_mac()
        except: 
            self.create_mac_file()    #download mac oui list and save to file as per the self.mac_file value
            self.load_mac()
            
        
    def create_mac_file(self):
        self.res = self.download_http(self.mac_file_url)
        self.list_to_file(self.res, self.mac_file, mode='w')
        
            
    def load_mac(self):    #load mac oui list from file
        import csv
        file = open(self.mac_file)
        reader = csv.reader(file)
        for row in reader:
            if row:
                raw = row[0]
                if '#' not in raw[0:1]:    #ignore comments
                    if raw[2] == ':' and raw[8] != ':':
                        mac_oui = raw[0:8]
                        mac_manf = str.rstrip(raw[9:17])
                        m = re.search(r'# (\w.+)', raw)
                        if m: mac_desc = (m.group(1))
                        else: mac_desc = ''
                        
                        #create mac_oui list 
                        res =  (mac_oui, mac_manf, mac_desc)
                        self.oui_list.append(res)
                        
                        
    def id_mac(self, mac):    #find mac
        if not mac: return 'No MAC address entered'
        if '.' in mac and len(mac) < 7: return 'Enter at least 7 chars - i.e. 0000.0c'
        if '.' not in mac and len(mac) < 8: return 'Enter at least 8 chars - i.e. 00:00:0c or 00-00-0c'
        mac = mac.upper()
        oui = ''

        if mac[4] == '.':    #mac format is 0000.0c07.ac03
            a = mac[0:2]
            b = mac[2:4]
            c = mac[5:7]
            oui = '%s:%s:%s' % (a, b, c)
        
        if mac[2] == ':': oui = mac[0:8]    #mac format is 00:00:0c:07:ac:03
            
        if mac[2] == '-': oui = mac[0:8].replace('-', ':')    #mac format is 00-00-0c-07-ac-03
        
        if oui:
            for row in self.oui_list:
                if row[0] == oui: return row[1], row[2]    #return on exact match
            
        return '', ''    #return empty values if no match or unknown format
        
        

        
if __name__ == "__main__":
    x = Mac()
    while 1:
        q = raw_input('\nEnter MAC address >>> ')
        if 'q' in q or 'exit' in q: break
        res = x.id_mac(q)
        if  type(res) is tuple: print '\nVendor details:  %s    %s' % (res[0], res[1])
        else: print '\n%s' % res
        
