import net, os
from subprocess import Popen
from tools import Tools

class SecureCRT(Tools):
    def __init__(self, hostname, ip_address, path=''):
        Tools.__init__(self)
        """
        This class is designed to create and use session files for Secure CRT 
        by cloning and modifying a pre made template session file.
        
        This class will add a new line (1) to a pre-made template file 
        by catenating self.ip_text and self.ip_address and saving the file 
        with hostname.ini in the relavent folder
        
        Template files must be prepared manually by making a session of each 
        connection type, including auto login credentials (if required)
        
        The process to create session template files and target directory's is as follows:
        1) Open secure crt and make a new session
        2) Go to folder C:\Program Files\SecureCRT\Sessions and open the session file in a text editor
        2) Create a blank first line in the file
        3) Remove the line containing S:"Hostname"=
        4) Save a template file for each connection type i.e. telnet.ini, ssh.ini, ssh2.ini
        5) Create output folders for each connection type in C:\Program Files\SecureCRT\Sessions
            i.e. C:\Program Files\SecureCRT\Sessions\telnet
                  C:\Program Files\SecureCRT\Sessions\ssh
                  C:\Program Files\SecureCRT\Sessions\ssh2
      
        Usage of the class:
        connection_type options are [telnet, ssh, ssh2]
        new connection types can be added by creating a folder and template file
        hostname is used to write the name of the session file
        ip_address is inserted into the session file and controls the connectivity
        
        session creation example:
        from python shell
        >>>import session
        >>>x = session.SecureCRT('ssh', 'my_router', '10.1.1.1')
        >>>x.make_session()
        
        session usage example:
        from windows command prompt
        c:\>securecrt /S "\ssh\my_router"
        
        from python shell
        >>>x.launch_session()
        
        Tested on Win XP with Python 2.7
        (c) 2012 - 2014 Intelligent Planet Ltd
        """
        
        #passed in class values
        self.hostname = hostname
        self.ip_address = ip_address
        self.path = path
        
        #test connection_type
        if self.ip_address != '0.0.0.0': self.connection_type = self.test()
        else: self.connection_type = ''
        
        #file name and path values
        self.file_extension = '.ini'
        if not self.path: 
            self.path = 'C:/Program Files/SecureCRT/Sessions/'
            self.default = 1
        self.output_path = self.path + self.connection_type + '/'
        self.output_file_name = self.output_path + self.hostname + self.file_extension
    
    
    def make(self):
        """
        A function designed to create the session text for a session.ini file
        and save the text into a new file in the following location:
        C:/Program Files/SecureCRT/Sessions/[connection type]/[hostname].ini
        i.e. C:/Program Files/SecureCRT/Sessions/ssh/my_router.ini
        """
        
        #read the session template
        self.session_template = open(self.path + self.connection_type + self.file_extension).read()
        
        #catanate the template and ip address
        self.ip_text = 'S:"Hostname"='
        self.output_text = self.ip_text + self.ip_address + self.session_template
        
        #write a new session file in the correct folder
        outfile = open(self.output_file_name, 'w')
        outfile.write(self.output_text)
        outfile.close()
        #print 'creating file', self.output_file_name
        
        
    def launch(self):
        """
        A function designed to open the session file that 
        was previously created with self.make_session()
        
        Uses Popen to open the session via windows command line
        Caveat - Tested on Win32 platforms only
        
        manual example of the operation:
        Popen('securecrt /S "\ssh\my_router"')
        
        Note - the string creation is in two parts as issues seen 
        with multiple backslash chars and string substitution
        \\\ is escape and \\ which is needed for Popen
        this ends up as single \ when the string passed from
        Popen to win cmd
        """
        
        #build the command string and execute it
        try: 
            if self.default: part_a = 'securecrt /S "\\\%s' % (self.connection_type)
        except: 
            path = self.path.split('/sessions/')[0]
            part_a = 'securecrt /f "%s" /S "%s' % (path, self.connection_type)
        
        part_b = '%s"' % (self.hostname)
        cmd = "Popen('%s\\\%s')" % (part_a, part_b)
        #print cmd
        exec(cmd)
        
        
    def test(self, verbose=1):
        """
        A function design to determine the connection_type (telnet, ssh1 or ssh2) and the
        authentication type (bt or produban)
        
        Method of testing is:
        1) Open port 23 and 22 to the device and read the banner
        2) Look for BT or PROD in the text and return the self.connection_type
        3) If banner reading can not determine the type, use pre configured string
            matches on parts of the self.hostname text and return the self.connection_type
        4) if the type can not be determined return 'fail'
        """
        
        bt_host = ['san-b', 'san-h', 'san-t', 'ab-h', 'san-d', 'ab-bbg', 'alg-1004', 'alg-1002', 'alg-1003', 'alg-1004', 'alg-1005', 'alg-1009', 'alg-101']
        bt_banner = [' bt ', 'british', 'telecommunications', 'BT', 'British', 'Telecommunications']
        prod_banner = ['prod', 'grupo']
        ssh2_list = ['2', '1.99']
        
        con = net.Net()
        
        #get the bt enable password and load it into the windows clipboard
        try:
            res = open('h:/config/btpw').read()
            self.btpw = 'echo %s| clip' % res
        except: self.btpw = 'echo error| clip'
        
        
        #Telnet test
        self.port = 23
        res = con.test_port(self.port, self.ip_address)
        if 'fail' not in res: 
            
            if verbose >0: print res
        
            for item in bt_banner:
                if item in res: 
                   self.send_clip(self.btpw)
                   return 'bt'
            
            for item in prod_banner:
                if item in res.lower(): return 'telnet'
        
        #fallback on hostname recognition and use telnet if a bt device
        for item in bt_host:
            if item in self.hostname.lower(): 
                self.send_clip(self.btpw)
                return 'bt'
            
            
        #SSH test    
        self.port = 22
        res = con.test_port(self.port, self.ip_address)
        if 'fail' not in res: 
            res = res.lower()
            if verbose >0: print res
            
            for item in ssh2_list:
                if item in res: return 'ssh2'
        
            if len(res) > 0: return 'ssh'
            
        print 'using default telnet'
        return 'telnet'
        
