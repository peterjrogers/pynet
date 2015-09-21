import telnetlib, time, os, getpass
from tools import Tools

try: import paramiko
except: pass

class Vty(Tools):
    def __init__(self, ip, name, port, auth_con=''):
        Tools.__init__(self)
       
        self.ip = ip
        self.name = name
        self.port = port
        self.auth_con = auth_con
        
        self.verbose = 1
               
        self.telnet_timeout = 2
        self.telnet_cmd_timeout = 5
        self.telnet_sleep = 0.1
       
        self.path = os.getcwd() + '\\'
        self.ssh_key_file = self.path +  'ssh_host_keys'
        self.more = '--More--'
        
        
    ##### TTY Auth #####
        
    def auth_produban(self):
        if not self.auth_con.tacacs_user: self.auth_con.auth_tacacs()
        
        self.username = self.auth_con.tacacs_user
        
        if not self.auth_con.tacacs_password: self.password = getpass.getpass('Enter TACACS Password: ')
        else: self.password = self.auth_con.tacacs_password
        
    def auth_bt(self):
        if not self.auth_con.bt_user: self.auth_con.auth_bt()
        
        self.username = self.auth_con.bt_user
        self.password = self.auth_con.bt_password
        
    def auth_pi(self):
        self.username = 'pi'
        self.password = 'raspberry'
    
    ##### Telnet Client #####
    
    def telnet_init(self, ip='', port=''):
        if not ip: ip = self.ip
        if not port: port = self.port
        
        try: self.telcon = telnetlib.Telnet(ip, port, self.telnet_cmd_timeout)
        except socket.error, e:
            if self.debug > 0: return (self.error, 'telnet_init', e)
           
           
    def telnet_login(self, user='', passw=''):
        if not user: user = self.username
        if not passw: passw = self.password
        
        self.telnet_read_until(self.telnet_login_text, user, 0)    #login
        self.telnet_read_until(self.telnet_pass_text, passw)    #password
        
        res = self.telcon.expect(self.telnet_banner_list, self.telnet_cmd_timeout)
        self.res = res[2].split('\r\n')[-1]    #banner
        
    
    def telnet_read_until(self, match, cmd, hide=1):
        res = self.telcon.read_until(match, self.telnet_timeout)
        self.telcon.write(cmd + '\r\n')
        if self.verbose > 0: 
            if hide == 1: print res, '*' * len(cmd)
            else: print res,
            
            
    def trim_more(self, line):
        """ Strip out --More-- and \x08 from telnet output """
        try:
            #try: 
            #    pos = line.index(self.more)
            #    start = pos + len(self.more)
            #except: start = 0
            out = ''
            for item in line:
                if ord(item) != 8: out += item
            return out
            
        except: return line
       
       
    def telnet_cmd(self, cmd):
        out = self.res
        self.telcon.write(cmd + '\r\n')
        res = self.telcon.expect(self.telnet_banner_list, self.telnet_cmd_timeout)
        out += res[2]
        while res[0] == 1:    #matched on '--More--'
            self.telcon.write(' ')
            out += '\r\n'
            res = self.telcon.expect(self.telnet_banner_list, self.telnet_cmd_timeout)
            #print res
            #out += res[2]
            out += self.trim_more(res[2])
       
        #if self.verbose > 0: print out
        return out
           
       
    def telnet_exit(self):
        self.telcon.write(self.telnet_exit_text + '\r\n')
        self.telcon.close()
        
    
    def telnet_cisco(self):
        self.telnet_login_text = 'Username: '
        self.telnet_pass_text = 'Password: '
        self.telnet_exit_text = 'q'
        self.telnet_banner_list = ['\d+>', '--More--', '\d+#']
    
    
    def telnet_test(self):
        print 'test'
        self.telnet_cisco()
        self.telnet_init()
        res = self.telcon.read_until('zzz', 1)
        if not res: return
        bt_host = []
        bt_banner = [' bt ', 'british', 'telecommunications', 'bt', 'british', 'telecommunications']
        prod_banner = ['prod', 'grupo']
        
        for item in bt_banner:
            if item in res.lower():
                self.auth_bt()
                if self.verbose > 0: print 'BT Cisco Telnet Detected'
                return
        
        for item in bt_host:
            if item in self.name.lower():
                self.auth_bt()
                if self.verbose > 0: print 'BT Cisco Telnet Detected'
                return
            
        for item in prod_banner:
            if item in res.lower():
                self.auth_produban()
                if self.verbose > 0: print 'Produban Cisco Telnet Detected'
                return

      
    def telnet_go(self, cmd_list='sh snmp loc', ip='', port='', test=1):
        try:
            if 'str' in str(type(cmd_list)): cmd_list = [cmd_list]    #convert single command str to list
            self.out = []
       
            if test > 0: self.telnet_test()
            
            self.telnet_init(ip='', port='')
            self.telnet_login()
       
            for item in cmd_list:
                res = self.telnet_cmd(item.lstrip())
                self.out.append(res)
           
            self.telnet_exit()
       
            if self.out:
                self.telnet_out = [x.split('\r\n') for x in self.out]
                
        except: return 'Failed to connect'
           
           
    ##### SSH Client #####
   
    def ssh_init(self, ip='', ports='', user='', passw=''):
        if not ip: ip = self.ip
        if not ports: ports = self.port
        if not user: user = self.username
        if not passw: passw = self.password
        
        #self.ssh_key_load()
        self.ssh_banner = '\n' + self.name + '#'
       
        self.sshcon = paramiko.SSHClient()
        self.sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshcon.connect(ip, port=ports, username=user, password=passw, allow_agent=False, look_for_keys=False)
       
       
    def ssh_cmd(self, cmd):
        stdin, stdout, stderr = self.sshcon.exec_command(cmd)
        return stdout#.readlines()
     
       
    def ssh_exit(self):
        self.sshcon.close()
       
       
    def ssh_key_load(self):
        self.ssh_keys = paramiko.HostKeys()
        try: self.ssh_keys.load(self.ssh_key_file)
        except IOError, e:
            if 'No such file' in str(e): self.ssh_keys.save(self.ssh_key_file)
       
       
    def ssh_go(self, cmd_list='sh log'):
        try:
            if 'str' in str(type(cmd_list)): cmd_list = [cmd_list]    #convert single command str to list
            self.ssh_out = []
       
            for cmd in cmd_list:
                self.ssh_init()
                res = self.ssh_cmd(cmd)
                self.ssh_out.append(self.ssh_banner + cmd) 
                for line in res:
                    line = line.strip('\r\n')
                    self.ssh_out.append(line)
                self.ssh_exit()
                time.sleep(1)
                
            if self.verbose > 0: self.view(self.ssh_out)
            #self.ssh_exit()

        except: return 'failed to connect'
        
        
    
