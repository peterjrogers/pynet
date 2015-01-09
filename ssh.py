import paramiko, os
from tools import Tools
from vty3 import Vty

class Ssh(Tools, Vty):
    def __init__(self, ip, hostname, out_dict='', auth_con=''):
        Tools.__init__(self)
        Vty.__init__(self, hostname, out_dict)
        """
        interface to the paramiko open ssl module
        """
       
        self.ip = ip
        self.hostname = hostname.lower()
        self.port = 22
        self.auth_con = auth_con
        self.user = ''
        self.password = ''
        
        self.path = os.getcwd() + '\\'
        self.debug_file = self.path + self.hostname + '_ssh_debug.log'
        
        self.newline = '\r\n'
        
        self.verbose = 1
        
        
    def start_debug(self):
        """ start a paramiko debug log file for this session """
        paramiko.util.log_to_file(self.debug_file)
        
        
    def view_debug(self):
        """ view a paramiko debug log file for this session """
        print open(self.debug_file).read()
        
        
    def init_con(self):
        """ open the ssh session """
        try:
            self.con = paramiko.SSHClient()
            self.con.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.con.connect(self.ip, self.port, self.user, self.password)
        except BaseException, e: return e
        
        
    def exec_cmd(self, command):
        """ execute the command and return stdin, out, error as class objects"""
        try: self.stdin, self.stdout, self.stderr = self.con.exec_command(command)
        except BaseException, e: return e
        
            
    def write(self, command):
        """ send a subcommand after exec_cmd """
        try: self.stdin.write(command)
        except BaseException, e: return e
       
        
    def flush(self):
        """ flush the stdin buffer after using write """
        try: self.stdin.flush()
        except BaseException, e: return e
        
            
    def read(self):
        """ read from stdout after exec_cmd """
        try: 
            self.read_out = self.stdout.read()
            self.split_out = self.read_out.split(self.newline)    #convert from string to list
        except BaseException, e: return e
             
        
    def close(self):
        """ close the session started with init_con """    
        try: self.con.close()
        except BaseException, e: return e
        
        
    def check_auth_con(self):
        """ If auth_con is not passed in then start a new auth instance for this session """
        if not self.auth_con:
            import auth
            self.auth_con = auth.Auth()
            self.auth_con.auth_tacacs()
                
                
    def check_auth(self):
        """
        if self.user / self.password are blank then 
        get user / password via auth module
        """
        if not self.user:
            self.check_auth_con()
            self.user = self.auth_con.tacacs_user
                
        if not self.password:
            self.check_auth_con()
            self.password = self.auth_con.tacacs_password  
    
