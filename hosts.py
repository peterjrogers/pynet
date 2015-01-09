

class Hosts():
    def __init__(self, verbose=0):
        """
        Generator function to iterate the windows host file
        
        Tested with Python ver 2.7.2 on Win7 & Win XP
        (c) 2012 - 2014 Intelligent Planet Ltd
        """

        self.verbose = verbose
        #self.load_file = 'C:/WINDOWS/system32/drivers/etc/hosts'
		#path = os.getcwd() + '\\'
        
    
    def get_hosts(self, cfile):
        file = open(cfile, 'rU')
        for row in file:
            if row:
                if '#' not in row[0]:
                    raw = row.lstrip().rsplit()
                    try:    
                        self.ip = raw[0]
                        self.host = raw[1].lower()
                        
                        res = row.find('#')
                        if res != -1: self.desc = row[res:].rstrip()
                        else: self.desc = ''
                        
                        yield self.host, self.ip, self.desc
                            
                    except: pass
                    
                        
