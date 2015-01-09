from tools import Tools
import pickle

class Show(Tools):
    def __init__(self):
        Tools.__init__(self)
        """
        Cisco show command parse tool and Db viewer
        
        sh ip int brief format is:
        ['Interface', 'IP-Address', 'OK?', 'Method', 'Status', 'Protocol']
        
        Dict format example is:
        self.dict_db[self.hostname] = {}
        self.dict_db[self.hostname][command] = {}
        self.dict_db[self.hostname][command][interface] = {}
        self.dict_db[self.hostname][command][interface][ip-address] = value
        """
        
        self.verbose = 0
        ### set the path to the log and db files ###
        try: self.path = 'H:/crt/sessions/'
        except: self.path = 'C:/Program Files/SecureCRT/Sessions/'
        
        self.load_file = self.path + 'log'
        self.db_file = self.path + 'show_db'
        self.load_dict()
        
        self.classify_dict = {'sh ip int brief': ['Interface', 'IP-Address']}
        
        
    def load_dict(self):
        try:    #load the dict file
            file = open(self.db_file, 'rb')
            self.dict_db = pickle.load(file)
        except: self.dict_db = {}
        finally: file.close()
        
        
    def read_file(self):
        self.operate = 0    #this will be non zero when a header is identified
        file = open(self.load_file, 'rU')
        for row in file:
            if row:
                if '#' in row: 
                    self.proc_cmd(row, '#')
                    out = row.split('#')
                
                elif '>' in row: 
                    self.proc_cmd(row, '>')
                    out = row.split('>')
                    
                else: out = row.split()
                if out: yield out
                
                
    def proc_cmd(self, row, symbol):
        try:
            self.hostname = row.split(symbol)[0]
            self.command = row.split(symbol)[1].rstrip()
            self.header = self.classify_dict[self.command]
            self.operate = 1    #will only reach this point if a dict entry is found for the command
            self.build_dict()
            if self.verbose > 0: print self.hostname, self.command, self.header, self.operate
        except: print 'failed to recognise the command %s' % self.command
        
        
    def main(self):
        try:
            start = 0
            gen = self.read_file()
        
            while 1:
                row = gen.next()
                if self.verbose > 0: print '\n', row
                if self.operate > 0 and start == 1:    #start processing the rows as records
                    self.pos = 0
                    for item in row:
                        if self.pos == 0:
                            key = row[0]
                            self.dict_db[self.hostname][self.command][key] = {}
                        elif self.pos < len(self.header):
                            self.dict_db[self.hostname][self.command][key][self.header[self.pos]] = row[self.pos]
                            if self.verbose > 0: print self.header[self.pos], row[self.pos], self.pos

                        self.pos += 1
                
                if row[0] in self.header[0] and row[1] in self.header[1]: start = 1
        
        except: pass
         
        
    def build_dict(self):
        try: self.dict_db[self.hostname]
        except: self.dict_db[self.hostname] = {}
        
        try: self.dict_db[self.hostname][self.command]
        except: self.dict_db[self.hostname][self.command] = {}
        
        
    def view(self):
        for host in self.dict_db.keys():
            print host.upper()
            for command in self.dict_db[host].keys():
                print '%s' % (command)
                print
                for interface in self.dict_db[host][command].keys():
                    print interface,
                    for item in self.dict_db[host][command][interface].keys():
                        print self.dict_db[host][command][interface][item], '    ',
                            
                    print

        
        
        
    
      
        
