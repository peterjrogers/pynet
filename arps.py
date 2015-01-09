import pickle, sys, os
from mac import Mac
from mnet import Mnet


class Arp(Mnet, Mac):
    def __init__(self):
        Mnet.__init__(self)
        Mac.__init__(self)
        
        """
        Arp testing tools
        
        # new dict format
        # arp_dict = {}
        # arp_dict['b0096'] = {}
        # arp_dict['b0096']['Vlan200'] = {}
        # arp_dict['b0096']['Vlan200']['10.67.6.81_0000.0c07.acc9'] = {}
        # arp_dict['b0096']['Vlan200']['10.67.6.81_0000.0c07.acc9']['ip'] = '10.67.6.81'
        # arp_dict['b0096']['Vlan200']['10.67.6.81_0000.0c07.acc9']['vendor'] = 'Cisco'
        # arp_dict['b0096']['Vlan200']['10.67.6.81_0000.0c07.acc9']['desc'] = 'hsrp_gw'
        # arp_dict['b0096']['Vlan200']['10.67.6.81_0000.0c07.acc9']['dns_name'] = ''
        # arp_dict['b0096']['Vlan200']['10.67.6.81_0000.0c07.acc9']['port_scan'] = {'22': ('SSH-2.0-Cisco-1.25\n',), '23': ('http hello'), '80': ('fail', 'timed out')}
        # arp_dict['b0096']['Vlan200']['10.67.6.81_0000.0c07.acc9']['ping'] = '38 ms'
        # arp_dict['b0096']['Vlan200']['10.67.6.81_0000.0c07.acc9']['date'] = '2013-04-08'
        # arp_dict['b0096']['Vlan200']['10.67.6.81_0000.0c07.acc9']['time'] = '00:14:19'
        
        new nexus format
        Address         Age       MAC Address     Interface
        172.19.167.5    00:00:57  0001.d7e8.0046  Vlan167         
        """
        
        self.verbose = 1
        self.path = os.getcwd() + '\\'
        self.cfile = self.path +  'r++'
        self.db_file = self.path + 'arp_db'
        self.mping_load_file = '//an/produban/Systems/Comms/Network Operations\Software\Multi Ping 1 & 2\R++ load.txt'
        self.ip_index = {}
        self.mac_index = {}
        self.name_index = {}
        self.branch_list = []
        self.test_list = []    #just the devices in current test run
        self.test_ip = []
        self.report_out = []
        self.nexus = 0
        
        try:    #load the arp dict file
            self.arp_file = open(self.db_file)
            self.arp_dict = pickle.load(self.arp_file)
            self.arp_file.close()
        except: self.arp_dict = {}
        
        self.make_index()
    
    
    def display_by_key(self, key):    #display the records for a primary key 
        
        try: self.arp_dict[key]    #check if the key exists
        except: return 'key fail'
        
        print '\n IP Address      Branch             MAC             Intf         Delay       Vendor      Hostname\n'
        vlan_list =  self.arp_dict[key].keys()
        for vlan in vlan_list:
            ip_mac_list = self.arp_dict[key][vlan].keys()
            for ip_mac in ip_mac_list:
                ip = ip_mac.split('_')[0]
                mac = ip_mac.split('_')[1]
                vendor = self.arp_dict[key][vlan][ip_mac]['vendor']
                ping = self.arp_dict[key][vlan][ip_mac]['ping']
                date = self.arp_dict[key][vlan][ip_mac]['date']
                time = self.arp_dict[key][vlan][ip_mac]['time']
                try:
                    dns_name = self.arp_dict[key][vlan][ip_mac]['dns_name']
                except: dns_name = ''
                
                print '%s%s  %s%s  %s  %s%s %s%s %s%s %s ' % (ip, self.space(ip, 16), key, self.space(key, 16), mac, vlan, self.space(vlan, 25), ping, self.space(ping, 13), vendor, self.space(vendor, 10), dns_name)
                
                
    def list_keys(self):
        key_list = self.arp_dict.keys()
        key_list.sort()
        for key in key_list: print key.upper()
        
        
    def delete_key(self, key):
        #delete a site / device level dict - i.e. arp_dict['b0096'] = {}
        print 'deleting records for site id / device: ', key
        try: 
            self.arp_dict[key]
            del self.arp_dict[key]
            self.save_dict()
        except: pass
          
    
    def search_ip(self, ip_address, like=''):
        #search the dict for an exact IP or MAC address match and return the key, interface and ip_mac to access the record
        key_list = self.arp_dict.keys()
        for key in key_list:
            interfaces = self.arp_dict[key].keys()
            for interface in interfaces:
                ip_macs = self.arp_dict[key][interface].keys()
                for ip_mac in ip_macs:
                    mac = ip_mac.split('_')[1]
                    ip = self.arp_dict[key][interface][ip_mac]['ip']
                    if ip_address == ip: return key, interface, ip_mac
                    if ip_address == mac: return key, interface, ip_mac
                    
                    #no exact matches so search for partial matching
                    if like and ip_address in ip: print ip, self.space(ip, 17), key
                    elif like and ip_address in mac: print mac, self.space(mac, 17), ip, self.space(ip, 17), key
                    
    
    def display_key_int_mac(self, key, interface, ip_mac):
        print 'Site id', self.space('Site id', 12), key
        print 'Interface', self.space('interface', 12), interface
        print 'Mac', self.space('mac', 12), ip_mac.split('_')[1]
    
    
    def display_record(self, key, interface, ip_mac):
        field_list = self.arp_dict[key][interface][ip_mac].keys()
        for field in field_list:
            entry = self.arp_dict[key][interface][ip_mac][field]
            print field.capitalize(), self.space(field, 12), entry
    
    
    """
    def search_mac(self, mac):
        res = [x for x in self.name_index.keys() if mac in x]    #check for dns_entries
        if res: 
            out = []
            for key in res: out.append(self.name_index[key])
            return out
        
        return [x for x in self.mac_index.keys() if mac in x]
        
    
    def return_record(self, mac_key):
        out = {}
        res = self.mac_index[mac_key]
        dicts = self.arp_dict[res[0]][res[1]][mac_key]
        out['Branch'] = res[0]
        out['Interface'] = res[1]
        out['MAC'] = mac_key.split('_')[1]
        for item in dicts:
            out[item.capitalize()] = dicts[item]
            
        return out

    
    def view_records(self, mac):    #view records for searched dns name, mac or ip address
        res = self.search_mac(mac)
        for mac_key in res:
            self.view(self.return_record(mac_key))
            print
    """
    
        
    def load_arp(self):    #load a csv file and return a list
        import csv
        file = open(self.cfile)
        reader = csv.reader(file)
        if self.verbose > 0: print 'Analysing arp entries'
        
        for row in reader:
            if row:
                ip = ''
                rows = row[0]
                
                if self.verbose > 2: print rows
                
                if '#sh' in rows or '# sh' in rows: 
                    branch = rows.split('#')[0].lower()    #use router name as last resort
                if '>' in rows: branch = rows.split('>')[0].lower()    #
                if 'san' in rows: branch = rows[4:9]           #san uk branch
                if 'ab-h' in rows: branch = 'h' + rows[5:9]     #head office number
                if 'alg' in rows: branch = 'h' + rows[4:8]    #ALG head office number
                if 'bip' in rows: branch = 'b' + rows[4:8]       #BIP agency
                    
                try:
                    if branch not in self.arp_dict: self.arp_dict[branch] = {}
                    if branch not in self.branch_list: self.branch_list.append(branch)
                    if branch not in self.test_list: self.test_list.append(branch)
                except: pass
                
                if 'Glean' in rows: self.nexus = 1
                
                if 'Internet' in rows and 'Incomplete' not in rows:
                    ip = rows[10:25].rstrip()
                    interface = rows[61:len(rows)]
                    mac = rows[38:52]
                     
                if self.nexus == 1 and '.' in rows and 'Incomplete' not in rows.lower():
                    ip = rows.split()[0]
                    interface = rows.split()[3]
                    mac = rows.split()[2]
                    
                if ip:    
                    desc = self.classify(mac)
                    vendor = self.id_mac(mac)[0]
                    self.test_ip.append(ip)
                    
                    if interface not in self.arp_dict[branch]:
                        self.arp_dict[branch][interface] = {}
                        
                    #ip & mac format is '10.67.6.81_0000.0c07.acc9'
                    ip_mac = ip + '_' + mac
                    if ip_mac not in self.arp_dict[branch][interface]:
                        self.arp_dict[branch][interface][ip_mac] = {}
                        
                    self.arp_dict[branch][interface][ip_mac]['ip'] = ip
                    self.arp_dict[branch][interface][ip_mac]['vendor'] = vendor
                    
                    self.arp_dict[branch][interface][ip_mac]['date'] = self.date
                    self.arp_dict[branch][interface][ip_mac]['time'] = self.time
                    
                    if desc: self.arp_dict[branch][interface][ip_mac]['desc'] = desc
                    
                    if 'alarm' in desc or '.193' in ip: 
                        port_res = self.check_port(ip, 80)[1:3]
                        self.arp_dict[branch][interface][ip_mac]['port'] = port_res
                        
                    #update index dict's
                    self.ip_index[ip] = (branch, interface, ip_mac)
                    self.mac_index[ip_mac] = (branch, interface)
                    
                    if self.verbose < 2: sys.stdout.write('.')
                   
        print '\n'
        
        
    def classify(self, mac):    #clasify mac by user defined list
        if '0017.c5' in mac: return 'Alarm' 
        if '0021.b7' in mac: return 'Printer'
        if '0000.0c' in mac: return 'HSRP_Gw'
        if '001a.d4' in mac: return 'ATM'
        return ''
     
     
    #def views(self, filter=''): self.view_pretty(self.arp_dict, filter)    #view a single branch with filter
    
    
    def load_ping(self):
        res = self.mt_ping(self.test_ip)
        for key in res:
            ind = self.ip_index[key]
            self.arp_dict[ind[0]][ind[1]][ind[2]]['ping'] = str(res[key][2]) + ' ms'  
        
    
    def load_name(self):
        res = self.mt_dns_rlook(self.test_ip)
        for key in res:
            ind = self.ip_index[key]
            name = res[key]
            if 'fail' not in name: self.arp_dict[ind[0]][ind[1]][ind[2]]['dns_name'] = name
        
    
    def report(self, branch=''):
        self.report_out = []
        if branch: branch_list = [branch]
        else: branch_list = self.test_list
        
        rep = ['ping', 'vendor', 'dns_name', 'port_scan']
        
        print '\n IP Address      Branch        MAC        Intf            Delay      Vendor    Hostname\n'
        ip_list = sorted(self.ip_index)
        for ip in ip_list:
            ind = self.ip_index[ip]
            res = self.arp_dict[ind[0]][ind[1]][ind[2]]
            
            if ind[0] in branch_list:
                res_ping = res_vendor =  res_dns = res_port = ''
                
                for item in rep: 
                    try: 
                        if 'ping' in item: res_ping = res[item]
                        if 'vendor' in item: res_vendor = res[item]
                        if 'dns_name' in item: res_dns = res[item]
                        if 'port' in item: res_port = res[item]
                    except: pass
                    
                res_out = '%s%s  %s  %s  %s%s %s%s %s%s  %s%s %s ' % (ip, self.space(ip, 16), ind[0], ind[2].split('_')[1], ind[1], self.space(ind[1], 16), res_ping[:9], self.space(res_ping[:9], 10), res_vendor, self.space(res_vendor, 8), res_dns, self.space(res_dns, 20), res_port)
                self.report_out.append(res_out)
                print res_out
                
        
    def report_mping(self): self.list_to_file(self.report_out, self.mping_load_file, mode='w')
                
                
    def save_dict(self):
        try:
            self.arp_file = open(self.db_file, 'wb')
            pickle.dump(self.arp_dict, self.arp_file)
            self.arp_file.close()
        
        except: print 'error saving arp_dict'
            
            
    def make_index(self):    #make index for loaded arp_dict values
        self.branch_list = [x for x in self.arp_dict]
        for branch in self.branch_list:
            int_list = [x for x in self.arp_dict[branch]]
            for intf in int_list:
                mac_list = [x for x in self.arp_dict[branch][intf]]
                for mac in mac_list:
                    self.mac_index[mac] = (branch, intf)
                    
                    ip = self.arp_dict[branch][intf][mac]['ip']
                    self.ip_index[ip] = (branch, intf, mac)
                    
                    try:
                        dns = self.arp_dict[branch][intf][mac]['dns_name']
                        self.name_index[dns] = mac
                    except: pass
                    
                    if self.verbose > 2: print mac, branch, intf, ip, dns
                    
                    
    def save_report(self):
        q = raw_input('press s to save output to multi ping load file >>>')
        if 's' in q.lower(): self.report_mping()
                
            
    def arp_go(self):
        self.test_list = []    #just the devices in current test run
        self.load_arp()
        self.load_ping()
        self.load_name()
        self.save_dict()
        self.report()
        
                
if __name__ == "__main__":
    a = Arp()
    a.arp_go()
    end = raw_input('press enter to exit')
                    
