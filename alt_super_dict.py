from tools import Tools
import pickle

class Super_dict(Tools):
    def __init__(self):
        Tools.__init__(self)
       
        """
        Dictionary storage method
        Use # followed by csv fields to define headers e.g. #host, ip, model, serial number
       
        device dict = [key][user specified fields]
        
        Written by Peter Rogers
        (C) Intelligent Planet 2013
        """
       
        self.verbose = 1
        self.key_txt = 'key'
        self.space_size = 18
        self.index = []
       
        # define self.dict_file in sub class
       
       
    def open_dict(self):
        try:    #load the dict file
            file = open(self.dict_file, 'rb')
            self.dict_db = pickle.load(file)
            file.close()
        except: self.dict_db = {}
       
       
    def save_dict(self):
        try:
            file = open(self.dict_file, 'wb')
            pickle.dump(self.dict_db, file)
            file.close()
        except:
            if self.verbose > 0: print 'error saving dict'
        
           
    def load_csv(self, cfile):
        try: file = open(cfile, 'rU')
        except: return
        for row in file:
            if row:
                if '#' in row[0]: head = row.strip('\n').lower().split(',')    #['#Host', 'IP', 'MAC', 'Serial', 'Model', 'Location\n']
                else:
                    res = row.strip('\n').strip('"').rstrip(' ').lower().split(',')
               
                    self.add_key(res[0])
                    self.index.append(res[0])
               
                    pos = 0
                    for item in res:
                        if pos > 0:
                            if res[pos]:
                                try:
                                    self.dict_db[res[0]][head[pos]] = res[pos]
                                    try: 
                                        self.dict_db[res[pos]]
                                        #if entry exists prefix with unique name
                                        key =  str(res[pos]) + '      (' + str(res[0]) + ')'
                                        self.dict_db[key] = {}
                                        self.dict_db[key][self.key_txt] = res[0]    #index for searching info fields
                                        
                                    except: 
                                        #entry is unique
                                        self.dict_db[res[pos]] = {}
                                        self.dict_db[res[pos]][self.key_txt] = res[0]    #index for searching info fields
                                    
                                    #old method
                                    #self.dict_db[res[pos]] = {}
                                    #self.dict_db[res[pos]][self.key_txt] = res[0]    #index for searching info fields
                                except: print 'failed', res[pos], res[0], pos, len(res), len(head)
                        pos += 1
                        
                        
    def add_key(self, key):
        try: self.dict_db[key]    #add new entry for key if it does not exist
        except: self.dict_db[key] = {}
                       
                       
    def search_keys(self, txt): return [x for x in self.dict_db.keys() if txt in x]

       
    def list_view(self, clist):    #retreive the key for full record
        out = []
        
        try: clist.sort()
        except: clist = [clist]
        
        for entry in clist:
            try: res = self.dict_db[entry][self.key_txt]
            except: res = entry
            out.append(res)
        return out
       
       
    def search_list(self, txt):    #return matching keys
        return self.list_view(self.search_keys(txt))
        
        
    def display(self, txt, filter_list=''):    #display records
        res = self.search_list(txt)
        for item in res:
            print '\n', item.upper()
            self.view(self.display_view(item, filter_list))
       
       
    def display_view(self, txt, filter_list=''):    #format record for display
        self.out = []
        res = self.dict_db[txt]
        key_list = res.keys()
        for key in key_list:
            res_out = '%s%s %s%s' % (key.capitalize(), self.space(key, self.space_size), res[key].upper(), self.space(res[key], self.space_size))
            self.filter_view(key, filter_list, res_out)
        return self.out
        
        
    def filter_view(self, key, filter_list, res_out):    #filter can be reversed by removing not
        if key not in filter_list: self.out.append(res_out)
        
    
    def filter_view_in(self, key, filter_list, res_out):    #inclusive filter for wide data sets
        if key in filter_list: self.out.append(res_out)
       
       
    def views(self, filter=''): self.view_pretty(self.dict_db, filter)
    
    
    def index_filter(self, res):
        out = []
        for item in res:
            if item in self.index: out.append(item)
        return out
        
        
    def view_res(self, res):
        for item in res: print item.upper()
        
        
    def view_hide(self, res, hide, view_list):
        out = []
        txt = '%s entries hidden ? to view ' % hide
        q = raw_input(txt)
        if q == '?': 
            for item in res:
                if item not in view_list:
                    out.append(item)
            return self.search_out(out)
        
        return out
    
    
    def search_info(self, q, lo_limit=25, hi_limit=250):
        out = []
        res = self.search_keys(q)
        view_list = self.index_filter(res)
        len_res = len(res)
        len_view = len(view_list)
        hide = len_res - len_view
        
        if len_res > lo_limit:
            if len_view > 0:
                if len_view < hi_limit: out = self.search_out(view_list)# self.view_res(view_list)
                else: out = self.view_hide(res, len_res, [])
            
            elif len_res < hi_limit: out = self.search_out(res)#self.view_res(res)
            
            if hide > 0: temp = self.view_hide(res, hide, view_list)
                
        else: out = self.search_out(res)
        return out
        
        
    def search_out(self, res, space_size=24):
        out = []
        for item in res:
            key = self.search_list(item)[0]
            if item in self.index: print item.upper()
            else: print '%s %s %s' %  (key.upper(), self.space(key, space_size), item.upper())
            out.append(key)
        return out
       
   
    
