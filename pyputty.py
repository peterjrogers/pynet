import net, os
from subprocess import Popen, PIPE


class Putty():
    def __init__(self, ip_address):
        """
        To start a connection to a server called host:

        putty.exe [-ssh | -telnet | -rlogin | -raw] [user@]host

        e.g. c:\Temp\python_27>putty -ssh 22.98.162.114
        """
        
        #passed in class values
        self.ip_address = ip_address
        self.path = os.getcwd() +'\\'
        self.launch()
        
    
    
    def test(self):
        
        con = net.Net()
        
        #Telnet test
        self.port = 23
        res = con.test_port(self.port, self.ip_address)
        if 'fail' not in res: return 'telnet'
                    
        #SSH test    
        self.port = 22
        res = con.test_port(self.port, self.ip_address)
        if 'fail' not in res: return 'ssh'
            
        print 'using default telnet'
        return 'telnet'
        
        
    def launch(self):
        res = self.test()
        
        if 'telnet' in res: cmd = '%sputty -telnet %s' % (self.path, self.ip_address)
       
        if 'ssh' in res: cmd = '%sputty -ssh %s' % (self.path, self.ip_address)
        
        print cmd
        try: Popen(cmd)
        except: pass
        
