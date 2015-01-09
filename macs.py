from tools import Tools
import pickle, re, os

class Macs(Tools):
    def __init__(self):
        Tools.__init__(self)
        """
        MAC parse tool and Db viewer
        
        sh mac-add dyn
        vlan   mac address     type    learn     age              ports
        *  124  0021.5e97.7b34   dynamic  Yes         30   Te1/3
        
        2nd variation
        vlan   mac address     type    learn            ports
        *  112  0023.7d35.1470   dynamic  Yes   Po2
        
        3rd variation - 
        vlan   mac address     type        protocols               port
        201    000c.29e0.cd3e   dynamic ip,ipx,assigned,other GigabitEthernet2/9
        
        [mac][host_port_vlan][date]
        
        Tested with Python ver 2.7.2 on Win7 & Win XP
        (c) 2012 - 2014 Intelligent Planet Ltd
        """
        
        self.verbose = 0
        self.path = os.getcwd() + '\\'
        self.load_file = self.path + 'mac_load'
        self.db_file = self.path + 'mac_db'
        
        
        try:    #load the mac dict file
            file = open(self.db_file, 'rb')
            self.mac_dict = pickle.load(file)
        except: self.mac_dict = {}
        finally: file.close()
        
        self.mac_db_length = len(self.mac_dict)
        
        
    def load(self):
        file = open(self.load_file, 'rU')
        host = ''
        for row in file:
            if row:
                if '#' in row: host = row.split('#')[0]
                if '>' in row: host = row.split('>')[0]
                out = row.split()
                port = mac = vlan = ''
                
                if out:    #check for hex encoded data
                    for i in range(2):
                        try: int(out[0])
                        except: 
                            if out: out.pop(0)
                
                    try:
                        #if '*' in out[0]: out.pop(0)
                        print out
                        mac = out[1]
                        vlan = out[0]
                        port = out[len(out) -1]
                        int(vlan)    #test for number
                    except: print 'error', out
                
                entry =  '%s_%s_Vlan%s' % (host, port, vlan)    #host_port_vlan

                if mac and len(mac) == 14 and '.' in mac:
                    if self.verbose > 0: print mac, entry, '\n', row, '\n', out, '\n'
                    try: self.mac_dict[mac]
                    except: self.mac_dict[mac] = {}
                    self.mac_dict[mac][entry] = self.date

                        
    def views(self, filter=''): self.view_pretty(self.mac_dict, filter)    #filter based on exact match or like match within key
                    
                    
    def search(self, txt):    #return matching keys
        res = [x for x in self.mac_dict.keys() if txt in x]
        return self.display(res)
        
        
    def display(self, clist):    #format record for display
        out = []
        for mac in clist:
            key_list = self.mac_dict[mac].keys()
            for key in key_list:
                date = self.mac_dict[mac][key]
                entry = key.split('_')
                res_out = '%s  %s  %s%s %s%s  Date %s' % (mac, entry[0], entry[2], self.space(entry[2], 9), entry[1], self.space(entry[1], 16),  date)
                out.append(res_out)
        return out

          
    def save(self):
        try:
            file = open(self.db_file, 'wb')
            pickle.dump(self.mac_dict, file)
            file.close()
        except: print 'error saving mac_dict'
        
        
if __name__ == "__main__":
    m = Macs()
    m.load()
    m.save()
    end = raw_input('press enter to exit')
        
        
