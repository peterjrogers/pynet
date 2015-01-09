import os, platform

class Tools():
    def __init__(self):
        self.update_time()
       
    ##### default interface for class(s) #####
       
  
    def var(self): print self.tree_var()
  
    def cmd(self): print self.tree_method()
      
    def ls(self): self.view(dir(self))
   
   
    ##### Class variable and method viewing #####
  
    def tree_var(self):    #return a str of variable names and values
        msg = ''
        for item in dir(self):
            cmd = 'res = str(self.%s)' % (item)
            exec(cmd)
            if 'method' not in res:
                if 'list' not in item and 'dict' not in item:
                    if res: msg += str(item) + ' ' + res + '\n'
        return msg
      
      
    def tree_method(self):    #return a str of method names
        msg = ''
        for item in dir(self):
            cmd = 'res = str(self.%s)' % (item)
            exec(cmd)
            if 'method' in res: msg += str(item) + '\n'
        return msg
      
      
    def view(self, clist):    #view a list or dict
        try:
            if 'dict' in str(type(clist)):
                self.view_dict(clist)
                return
           
            for item in clist:
                if 'list' in str(type(item)): self.view(item)    #recurse multi level lists
                else: 
                    if 'str' in str(type(clist)): 
                        print clist
                        return
                    else: print item
                    
       
        except: return
       
       
    def view_dict(self, cdict):    #view a dict
        for key in cdict: 
            print key, self.space(key, 15), cdict[key]
        
        
    def view_sorted(self, cdict):    #view a sorted dict
        for key in sorted(cdict.keys()): print key, cdict[key]
        
    
    def view_pretty(self, cdict, filter=''):    #view formatted data structure
        import pprint
        pp = pprint.PrettyPrinter(indent=1)
        if not filter: pp.pprint(cdict)
        else: 
            try: pp.pprint(cdict[filter])
            except: 
                keys = [x for x in cdict.keys() if filter in x]
                out_dict = {}
                for key in keys:
                    out_dict[key] = cdict[key]
                pp.pprint(out_dict)
        
        
    def space(self, word, base=5, sep=' '): return sep * (base - len(str(word)))    #create blanks for str formatting
                 
      
    def tree_list(self):    #view all lists
        for item in dir(self):
            cmd = 'res = self.%s' % (item)
            exec(cmd)
            test = type(res)
            if 'list' in str(test):
                print item
                self.view(res)
                print
               
   
    def file_stamp(self):
        import datetime
        now = datetime.datetime.now()
        self.time_stamp = now.strftime("__%H-%M-%S__%d-%m-%Y__")
       
   
    def date_time(self):
        import datetime
        now = datetime.datetime.now()
        res = now.strftime("%Y-%m-%d,%H:%M:%S,%b,%d,%H")
        self.time_res = res.split(',')
        
        
    def update_time(self):
        self.date_time()
        self.date = self.time_res[0]
        self.time = self.time_res[1]
        self.month = self.time_res[2]
        self.day = self.time_res[3]
        self.hour = self.time_res[4]
        
        
    def list_to_file(self, clist, cfile, mode='w'):    #save the contents of a list to a file
        if not clist: return
        try: file = open(cfile, mode)
        except: file = open(cfile, 'w')
        pos = 0
        
        for item in clist:
            if 'list' in str(type(item)): #use recursion if list in list
                self.list_to_file(item, cfile, 'a')
            else:
                res = str(item) + '\n'
                if '--More--' not in res: file.write(res)
                
                
    def download_http(self, url, splits='\n'):    #download data and split into a list on (string specified or newline as default)
        import urllib2
        return urllib2.urlopen(url).read().split(splits)
                
                
    def ip_add(self, ip):
        res = ip.split('.')
        d = int(res[3])
        if d <= 253: 
            d += 1
            res.pop()
            res.append(str(d))
            return res[0] + '.' + res[1] + '.' + res[2] + '.' + res[3]
            
        else: return ip
        
        
    def ip_sub(self, ip):
        res = ip.split('.')
        d = int(res[3])
        if d >= 1: 
            d -= 1
            res.pop()
            res.append(str(d))
            return res[0] + '.' + res[1] + '.' + res[2] + '.' + res[3]
            
        else: return ip
        
        
    def viewwhois(self, txt, verbose=0):
        #http://www.whois.com/whois/2.122.172.83
    
        start = 0
        head_start = 0
        line = ''
        header = ''
        class_start = 0
        for item in txt:
            if item == '<': 
                header = '<'
                head_start = 1
                continue
        
            if item == '>': 
                header += item
                if verbose > 0: print header
                head_start = 0
                continue
            
            if head_start == 1: header += item
        
            if 'body' in header: start = 1
            if '/body' in header: return
            if 'whois_result' in header: class_start = 1
        
        
            if start == 1:
                if head_start == 0 and class_start == 1:
                    if '/div' in header: return
                    line += item
                    if '\n' in line: 
                        print line
                        line = ''

                        
    def view_http(self, txt, verbose=0):
        header = ''
        line = ''
        head_start = 0
        for item in txt:
            if item == '<': 
                header = item
                head_start = 1
                continue
        
            if item == '>': 
                header += item
                if verbose > 0: print header
                head_start = 0
                continue
                
            if head_start == 1: header += item
            else: line += item
            
            if '\n' in line:
                print line
                line = ''
                
                
    def send_clip(self, txt_string):
        """
        Send a string to the windows clipboard pipe feature
        """
        try: 
            win_ver = platform.platform().lower()
            if 'windows-7' in win_ver: os.system(txt_string)
        except: pass
            
            
            
