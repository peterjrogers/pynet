from super_dict2 import Super_dict
import net2, session3, hosts, os

hosts_con = hosts.Hosts()

class Device(Super_dict):
    def __init__(self):
        Super_dict.__init__(self)
       
        """
        Device db
       
        self.dict_db format is [hostname][ip  |  user specified fields]
        
        self.index is a list containing all hosts and is used to 
        resolve searches to a single host entry
        """
       
        self.path = os.getcwd() + '\\'
       
        self.device_file = self.path + 'Devices.csv'
        self.device_update_file = self.path + 'devices_updates.csv'
        self.bt_load_file = self.path + 'bt_Devices.csv'
        self.bt_update_file = self.path+ 'bt_device_updates.csv'
        self.win_host_file = 'C:/WINDOWS/system32/drivers/etc/hosts'
        self.alt_host_file = self.path + 'hosts'
       
        #self.dict_file = 'c:/device_db'
        
        self.device_load()
        self.load_hosts(self.win_host_file)
        self.load_hosts(self.alt_host_file)
       
       
    def device_load(self):
        
        self.load_csv(self.bt_load_file)
        self.load_csv(self.bt_update_file)
        self.load_csv(self.device_file)
        self.load_csv(self.device_update_file)
        
        
    def load_hosts(self, cfile):
        """
        get_hosts returns a tuple of hostsname, ip_address, description
        """
        try: 
            head = ['host', 'ip', 'desc']
            gen = hosts_con.get_hosts(cfile)
            while 1: 
                res = gen.next()
                if res[0] not in self.index:
                    self.add_record(head, res)
        except: pass

        
    def search(self):    #search the device db and return host and ip for single matching entry
        while True:
            q = raw_input('Search >>>')
            q = q.rstrip('\n').lower()
            
            if q: 
                res = self.search_func(q)
                
                if len(res) ==1:
                    self.display(res[0])
                
                
    def search_func(self, q, verbose=0):
        if q in self.index: res = [q]
        else:
            res = self.search_hash(q)
        
        self.host_list = []
        for item in res: self.display_host_search(item, verbose)
        if len(self.host_list) == 1: 
            res = self.host_list
            print 'unique match in DB\n'
        else: print '\n', len(res), 'Results from DB\n'
        return res
        
        
    def show_info(self, host): self.view(self.display(host))
        
        
    def display_host_search(self, txt, verbose=0):
        try:
            res = self.hash_index(txt)
            self.host = self.dict_db[res[0]]['host']
            
            try: 
                if self.host not in self.host_list:
                    self.host_list.append(self.host)
            except: pass
            
            self.ip = self.dict_db[res[0]]['ip']
            try: self.auth = self.dict_db[res[0]]['auth']
            except: self.auth =''
            try: self.port = self.dict_db[res[0]]['port']
            except: self.port = ''
            if verbose == 0: print '%s%s %s%s %s' % (self.host.upper(), self.space(self.host, 40), self.ip, self.space(self.ip, 18), txt.upper())
        except: pass
        
        
                   
                         
