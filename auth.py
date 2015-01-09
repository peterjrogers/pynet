import getpass

class Auth():
    def __init__(self):
    
        """
        Authentication methods are defined here
        the safest method is to use the memory
        resident password storage, password will
        be prompted upon first use & will remain
        until the terminal window is closed.
        
        Tested on Win XP with Python 2.7
        (c) 2012 - 2014 Intelligent Planet Ltd
        """
        
        self.auth_path = 'h:/config/'
        self.tacacs_user = ''
        self.tacacs_password = ''
        self.bt_user = ''
        self.bt_password = ''
        self.enable_password = ' '
    
    
    def auth_tacacs(self):
        ### Get TACACS user / password and store in memory
        
        try: self.tacacs_user = open(self.auth_path + 'user.txt').read()
        except: self.tacacs_user = raw_input('Enter TACACS Username:')
    
        try: self.tacacs_password = open(self.auth_path + 'pw').read()
        except: self.tacacs_password = getpass.getpass('Enter TACACS Password: ')
    
    def auth_bt(self):
        ### Get BT user / password and store in memory
        
        self.bt_user = 'user'
        try: self.bt_password = open(self.auth_path + 'btpw').read()
        except: self.bt_password = getpass.getpass('Enter BT Password: ')
        
    def auth_enable(self):
        ### Get Enable password and store in memory
        
        try: self.enable_password = open(self.auth_path + 'enable').read()
        except: pass
    
    
