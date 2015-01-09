import telnetlib, os
from tools import Tools
from vty3 import Vty

class Telnet(Tools, Vty):
    def __init__(self, ip='', hostname='', out_dict='', auth_con=''):
        Tools.__init__(self)
        Vty.__init__(self, hostname, out_dict)
        """
        interface to the the telnet library
        """
       
        self.ip = ip
        self.hostname = hostname.lower()
        self.port = 23
        
        self.auth_con = auth_con
        self.user = ''
        self.password = ''
        
        self.path = os.getcwd() + '\\'
        
        self.newline = '\r\n'
        self.space = ' '
        
        self.verbose = 1
        
        self.read_until_timeout = 2
        self.timeout = 5
        self.sleep = 0.1
        
        #set the values for Cisco as default
        self.login_text = 'Username: '
        self.password_text = 'Password: '
        self.exit_text = 'q'
        self.banner_list = ['\d+>', '--More--', '\d+#']
        self.more = '--More--'
        
        
    def start_debug(self):
        """ start a debug for this session """
        pass
        
        
    def view_debug(self):
        """ view a debug for this session """
        pass
              
        
    def init_con(self):
        """ open the telnet session """
        try: 
            self.con = telnetlib.Telnet(self.ip, self.port, self.timeout)
            self.login_con()
            self.prompt = self.prompt_con()
        except BaseException, e: return e
        
    
    def login_con(self):
        """ login to the telnet session by automating the input of user & pass """        
        self.read_until(self.login_text, self.user)    #enter self.user
        self.read_until(self.password_text, self.password)    #enter self.password
        
        
    def prompt_con(self):
        """ use after login to read past the banner mesage and capture the prompt """
        return self.con.expect(self.banner_list, self.timeout)[2].split(self.newline)[-1]    #return the last item of the text string
        
        
    def read_until(self, match, command):
        """ read until match and then write cmd to the socket """
        try:
            self.res = self.con.read_until(match, self.timeout)
            if self.res: self.write(command)
        except BaseException, e: return e
        
        
    def exec_cmd(self, command):
        """ execute the command and return as class objects"""
        try: self.write(command)
        except BaseException, e: return e
        
            
    def write(self, command):
        """ send a string to the telnet socket """
        try: 
            self.write_command = command
            self.con.write(self.write_command + self.newline)
        except BaseException, e: return e
        
            
    def read(self):
        """ read from telnet socket after exec_cmd """
        try: 
            self.read_out = ''#self.prompt
            self.read_res = self.con.expect(self.banner_list, self.timeout)
            self.read_out += self.read_res[2]
            self.read_more()
            self.split_out = self.read_out.split(self.newline)    #convert from string to list
        except BaseException, e: return e
        
        
    def read_more(self):
        """ look for the --More-- prompt on multi page output's - this negates the need for term len 0 """
        try:
            while self.read_res[0] == 1:    #expect matched the index of 1 in self.banner_list ('--More--')
                self.write(self.space)
                self.read_res = self.con.expect(self.banner_list, self.timeout)
                self.read_out += self.read_res[2]
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
            
            
    def test_me(self, cmd):
        self.init_con()
        self.exec_cmd(cmd)
        self.read()
        print self.read_out
        

