from tools import Tools
import time, os

class Batch(Tools):
    def __init__(self, dev_con='', cli_con=''):
        Tools.__init__(self)
        
        """
        Batch processing tools
        
        (c) 2012 - 2015 Intelligent Planet Ltd
        """
        import mnet, net
        self.mnet_con = mnet.Mnet()
        self.net_con = net.Net()
        
        self.path = os.getcwd() + '\\'
        self.clear()
        self.dev_con = dev_con
        self.cli_con = cli_con
        self.out_file = self.path + 'batch'
        self.time_wait = 1
        self.ttl = 35
        self.pent_hop = ''    #penultimate hop from the last traceroute performed
        self.batch_host_list = []    #hosts to perform the batch job on
        self.view_list = []    #result of the search results passed in from cli
        self.trace_dict = {}    #result of the traceroute
        self.ping_dict = {}    #used for ping test results
        self.host_dict = {}    #used for ip to hostname lookups
        self.dns_dict = {}    #used for dns lookups - both normal and reverse
        self.port_dict = {}    #used fort port test results
        self.vty_os = 'ios'
        self.verbose = 1
        self.tcp_port = 80
        self.sleep = 1
        self.ip = ''
        self.host = ''
        self.res = ''
        
        
        #info obtained from sh ver in self.vty_sh_ver()
        self.init_sh_ver()
        
        #describe the output format for a command
        self.cmd_transform = {
            'sh ip arp': ['Protocol', 'Address', 'Age', 'Hardware Addr', 'Type', 'Interface'],
            'sh mac address-table': ['vlan', 'mac address', 'type', 'ports'],
            'sh mac add ': ['vlan', 'mac address', 'type', 'protocols', 'port'],
            'sh mac-add': ['star', 'vlan', 'mac address', 'type', 'learn', 'age', 'ports'],
            'sh int desc': ['Interface', 'Status', 'Protocol', 'Description'],
            'sh ver': ['hostname', 'serial_number', 'reload_cause']
        }
        
        #describe the matching rule format to identify valid output - i.e. match word in pos
        #ios, catos & nxos are used for sh_ver
        self.cmd_rules = {
            'sh ip arp': ['internet', 0],
            'sh mac address-table': ['dynamic', 2],
            'sh mac add ': ['dynamic', 2],
            'sh mac-add': ['dynamic', 3],
            'sh int desc': ['up', 1],
            'ios': ['uptime', 0, 'processor board id', 3, 'system returned to rom by', 5],
            'catos': ['sh ver', 0, 'hardware version:', -1, 'system returned to rom by', 5],
            'nxos': ['device name', 2, 'processor', 3, 'reason:', 1]
        }
    
    
    def init_nexus(self):
        """
        help: Modify transform keys to make them specific to nexus NX-OS
        usage: batch init_nexus
        """
        self.cmd_transform['sh mac add '] = ['star', 'vlan', 'mac address', 'type', 'age', 'secure', 'ntfy', 'port']
        self.cmd_rules['sh mac add '] = ['dynamic', 3]
    
    
    def init_ios(self):
        """
        help: Modify transform keys to make them specific to IOS
        usage: batch init_ios
        """
        self.cmd_transform['sh mac add '] = ['vlan', 'mac address', 'type', 'protocols', 'port']
        self.cmd_rules['sh mac add '] = ['dynamic', 3]
    
    
    def init_sh_ver(self):
        """
        help: reset the host information obtained by running sh ver on the host
        usage: batch init_sh_ver
        """
        self.hostname = ''    
        self.serial_number = ''
        self.reload_cause = ''
        self.vty_os = 'ios'
    
    
    def clear(self): 
        """
        help: clear the batch host list
        usage: batch clear
        """
        self.batch_host_list = []
        
        
    def remove_in_host_list(self, txt):
        """
        help: perform a list comprehension on the batch host list and remove the host if 'txt' matches in any part
        usage: batch in [txt]
        example: batch in swd
        """
        res = [x for x in self.batch_host_list if txt in x]
        for host in res: self.pops(host)
        
        
    def remove_not_in_host_list(self, txt):
        """
        help: perform a list comprehension on the batch host list and remove the host if 'txt' is not in any part
        usage: batch not in [txt]
        example: batch not in lwd
        """
        res = [x for x in self.batch_host_list if txt not in x]
        for host in res: self.pops(host)
        
        
    def add(self):
        """
        help: add hosts from the search view into the batch host list
        usage: batch run add
        """
        for host in self.view_list:
            if host not in self.batch_host_list: 
                self.batch_host_list.append(host)
                print 'added %s' % host 

                
    def sub(self):
        """
        help: remove search view hosts from the batch host list
        usage: batch run sub
        """
        for host in self.view_list: self.pops(host)
                  
            
    def pops(self, host):
        """
        remove a host from the batch host list by specifying it (internal function)
        """
        try:
            pos = self.batch_host_list.index(host)
            self.batch_host_list.pop(pos)
            print 'removed %s' % host
        except: print 'error removing %s' % host
        
        
    def make_ip_list(self):
        """
        used to get a list of ip address from the batch host list
        """
        self.ip_list = []
        for host in self.batch_host_list:
            try: 
                key = self.dev_con.search_db[host]['key']
                ip = self.dev_con.dict_db[key]['ip']
                self.host_dict[ip] = host
                if ip not in self.ip_list: self.ip_list.append(ip)
            except: print 'error %s ip address not found' % host
                              
            
    def process_ping(self, res_dict):
        """
        used to display the result of the batch ping command
        format of return from mnet ping function is 172.22.117.1 (1, 1, 2, 241, '172.22.117.1')
        we make it look like this: 
        san-b0025-rtr-01     172.22.25.132   Recv: 0  Delay: timed out   From: -                Result: fail
        """
        self.host_result = {}
        for ip in res_dict:
            host = self.host_dict[ip]
            output = res_dict[ip]
            recv = output[1]
            delay = str(output[2])
            reply_from = output[4]
            ping_result = self.ping_success(recv, ip, reply_from)
            print '%s%s %s%s Recv: %d  Delay: %s%s  From: %s%s  Result: %s' % (host, self.space(host, 20), ip, self.space(ip, 15), recv, delay, self.space(delay, 10), reply_from, self.space(reply_from, 15), ping_result)
            self.host_result[host] = ping_result
                        
            
    def ping_success(self, recv, ip, reply_from):
        """
        Test that a packet is received from the target and not an intermediate router i.e. expired in transit
        """
        if recv == 1 and ip == reply_from: return 'ok'
        else: return 'fail'
        
        
    def ping(self):
        """
        help: perform a multi threaded ping on the hosts in the batch host list
        usage: batch ping     
        """
        try:
            self.make_ip_list()
            self.ping_dict = self.mnet_con.mt_ping(self.ip_list)
            self.process_ping(self.ping_dict)
        except: print 'error - use batch add to define a list of hosts to ping'
    
        
    def trace(self):
        """
        help: Run a multi threaded trace route and store the result in trace_dict
        example: batch trace
        mt_trace output is {1: [(self.ping_sent, self.ping_recv, self.ping_delay, self.ping_ttl, hop_ip, host_name)]}
        """
        
        self.make_ip_list()
        
        for ip in self.ip_list:
            res = self.mnet_con.mt_trace(ip, ttl=self.ttl)
            print res
            if res:
                try:
                    pent_index = len(res) - 1
                    self.pent_hop = res[pent_index][0][4]
                    self.trace_dict[ip] = {}
                    self.trace_dict[ip]['output'] = res
                    self.trace_dict[ip]['pent_hop'] = self.pent_hop
                except: pass
                
   
    def rlook(self):
        """
        help: perform a reverse lookup on the batch host list IP entries with the cli verify_ip function
        example: batch rlook
        output is ('172.22.25.135', 'san-b0025-l2s-01')
        """
        self.make_ip_list()
        for ip in self.ip_list:
            res = self.cli_con.verify_ip(ip)
            self.dns_dict[res[0]] = res[1]
            if self.verbose >  0: print res
            
        
    def mt_rlook(self):
        """
        help: perform a DNS reverse lookup on the batch host list IP entries with the multi threaded rlook function
        example: batch mt_rlook
        output is {'172.22.25.132': 'fail'}
        """
        self.make_ip_list()
        res = self.mnet_con.mt_dns_rlook(self.ip_list)
        for ip in res.keys():
            self.dns_dict[ip] = res[ip]
            if self.verbose >  0: print ip, res[ip]
            
            
    def mt_look(self):
        """
        help: perform a DNS name lookup on the batch host list entries with the multi threaded look function
        example: batch mt_look
        output is {'www.alliance-leicestercommercialbank.co.uk': '165.160.15.20'}
        """
        res = self.mnet_con.mt_dns_look(self.batch_host_list)
        for name in res.keys():
            self.dns_dict[name] = res[name]
            if self.verbose >  0: print name, res[name]
            
        
    def set_tcp_port(self, tcp_port):
        """
        help: set the self.tcp_port port number for use in the batch port command (default is 80)
        usage: set tcp port [tcp port number]
        example: set tcp port 80
        """
        try: self.tcp_port = int(tcp_port)
        except: print 'failed to set the port with', tcp_port
    
    
    def port(self):
        """
        help: perform a tcp port test on the ip address in the host list and on the port specified by self.tcp_port
        usage: batch port
        note: use 'set tcp port 23' to set the port first - default is 80
        
        example output from failure
        ('fail', 'socket_open', timeout('timed out',))
        
        example from successful port read 
        HTTP/1.1 404 Not Found
        Content-Type: text/html     
        """
        self.make_ip_list()
        for ip in self.ip_list:
            print 'trying port %d on %s' % (self.tcp_port, ip)
            res = self.net_con.test_port_front(self.tcp_port, ip)
            if self.verbose > 0: print res
            self.port_dict[ip] = res
            time.sleep(self.sleep)    #use 0.5 to 1 sec to avoid firewall blocks based on tcp session limit / sec
            
            
    def find_ip(self, host):
        """
        help: Find the IP address via the device class passed into the batch class
        usage: batch find_ip(host)
        example: batch find_ip('home-router')
        output is ip if a match is found or null
        """
        key = self.dev_con.search_db[host.lower()]['key']
        return self.dev_con.dict_db[key]['ip']
        
        
    def find_host(self, ip):
        """
        Find the hostname via the cli class function verify_ip which returns ip, hostname
        """
        return self.cli_con.verify_ip(ip)[1]
        
        
    def find_arp(self, ip):
        """
        Look for an arp entry in the db and return the record in format host, interface, ip_mac
        ('dswpcain01', 'Vlan21', '107.22.21.56_0050.56b5.1a6b')
        """
        return self.cli_con.arp_con.search_ip(ip)
        
    
    def find_port(self, ip , host): 
        """
        Find the port via the cli class function which returns text type, port number - i.e. bt, 23
        """
        return self.cli_con.test_session(host, ip)[1]
        

    def vty_connect(self, ip='', host='', cmd='', verbose=1):
        if not ip: ip = self.find_ip(host)
        if not host: host = self.find_host(ip)
        if verbose > 0: print 'connecting to %s with %s' % (host, ip)
        port = self.find_port(ip, host)
        time.sleep(self.time_wait)
        self.vty_out = self.cli_con.vty_session(ip, host, port, cmd)
        #if len(self.vty_out) == 1: self.vty_out = self.vty_out[0]    #telnet format fix
        
    
    def find_cmd_key(self, cmd):
        """
        Step through the cmd one char at a time until a unique cmd_transform key match is found
        batch trans key test sh mac address-table address 000b.5de3.7ee6
        """
        for pos in range(4, len(cmd)):
            key = [x for x in self.cmd_transform.keys() if cmd[:pos] in x]
            if len(key) == 1: return key[0]
        
        
    def vty_parse(self, ip='', host='', cmd='', verbose=1):
        """
        use cmd_transform and cmd_rules to determine which rows to process and return
        """
        cmd_key = self.find_cmd_key(cmd)
        print cmd_key
        transform = self.cmd_transform[cmd_key]
        rule_txt = self.cmd_rules[cmd_key][0]
        rule_pos = self.cmd_rules[cmd_key][1]
        print transform
        print rule_txt
        out = []
        self.vty_connect(ip=ip, host=host, cmd=cmd, verbose=1)
        if len(self.vty_out) == 1: self.vty_out = self.vty_out[0]    #telnet format fix
        for rows in self.vty_out:
            try:
                print rows
                row = rows.split()    ; print row
                if len(row) != len(transform): continue
                if row[rule_pos].lower() != rule_txt: continue
                out.append(row)
            except: pass
        return out
        
        
    def vty_sh_ver(self, ip):
       """
       information capture via sh ver command
       batch vty sh ver 172.22.25.132    #ios     
       batch vty sh ver 22.99.29.132    #nx-os
       batch vty sh ver 172.22.37.180    #catos
       """
       
       self.init_sh_ver()
       cmd = 'sh ver'
       self.vty_connect(ip=ip, host='', cmd=cmd, verbose=1)
       if len(self.vty_out) == 1: self.vty_out = self.vty_out[0]    #telnet format fix
       
       #detect os and setup the custom transforms
       self.vty_os = self.vty_id_os(self.vty_out)
       self.vty_set_transform(self.vty_out)
       
       transform = self.cmd_rules[self.vty_os]
       cmd_transform = self.cmd_transform[cmd]
       
       print self.vty_os
       print transform
       print cmd_transform

       return self.vty_parse_list(transform, cmd_transform)
       
       
    def vty_parse_list(self, transform, cmd_transform):
        """
        Parse a list of data using the data definition in transform
        data is already collected and located in self.vty_out
        pass in the cmd_transform list as out so the data can be placed in correct list index
        """
        out = range(len(cmd_transform))
        
        end = len(transform) -1
        for rows in self.vty_out:
            pos = 0
            key = 0    #index pos for out
            while pos < end:
                try:
                    if transform[pos] in rows.lower(): 
                        out.pop(key)
                        out.insert(key, rows.split()[transform[pos+1]])
                except: pass
                pos += 2
                key += 1
        return out
         
       
    def vty_id_os(self, vty_out):
        """
        Read the output from the sh ver command in vty_out and look for the following words
        IOS, NX-OS or NmpSW (CAToS)
        """
        for row in vty_out:
            if 'ios' in row.lower(): return 'ios'
            if 'nx-os' in row.lower(): return 'nxos'
            if 'nmpsw' in row.lower(): return 'catos'
            
            
    def vty_set_transform(self, vty_os):
        """
        setup the transform dict for the OS
        """
        if vty_os == 'nxos': self.init_nexus()
        if vty_os == 'ios': self.init_ios()
       
        
    def vty_test_arp(self, ip):    #batch vty test arp 172.22.25.132     107.22.28.6
        return self.vty_parse(ip=ip, host='', cmd='sh ip arp', verbose=1)
        
        
    def vty_test_cmd(self, ip, cmd):    
        """
        #arp entry tests
        batch vty test cmd sh ip arp 107.22.21.128,107.22.28.6    #1 - 0050.56b5.29ac
        batch vty test cmd sh ip arp 10.6.36.189,10.13.251.82
        batch vty test cmd sh ip arp 180.100.120.92,107.22.28.6
        
        #mac entry tests
        batch vty test cmd sh mac add dynamic,107.22.28.6
        batch vty test cmd sh mac add add 0050.56b5.29ac,107.22.28.6    #2 - GigabitEthernet2/13
        
        batch vty test cmd sh mac address-table dyn,22.98.166.14
        batch vty test cmd sh mac address-table add 442b.03ee.43b3,22.98.166.14
        
        batch vty test cmd sh mac-add dyn,172.19.128.65
        batch vty test cmd sh mac-add add 0016.9cf4.9c00,172.19.128.65
        
        #need to run the sh ver as first cmd to setup the transforms
        batch vty sh ver 22.98.78.65
        batch vty test cmd sh mac add dynamic,22.98.78.65    #nxos
        
        #int desc tests
        batch vty test cmd sh int desc,107.22.28.6
        """
        return self.vty_parse(ip=ip, host='', cmd=cmd, verbose=1)
        
        
    def vty_sh_int_desc(self, ip):
        """
        help: Perform a sh int desc
        usage: batch run vty_sh_int_desc(ip)
        example: vty_sh_int_desc 10.1.1.1
        
        Used a fixed width parse based on the label as below
        Interface                      Status         Protocol Description
        """
        pass
        
        
    def help(self):
        """
        View the help and example information for each function in the class
        """
        for item in dir(self): 
            try: 
                exec('self.help_res = self.' + item + '.__doc__')
                if 'help' in self.help_res: print '\n', item, '\n', self.help_res
            except: pass
            
                    
    def run(self, cmd):
        """
        help: Execute a function or assign a variable within the local scope
        usage: batch run [cmd]
        example: batch run ls
        """
        self.res = ''
        #check for assign statement
        if '=' in cmd: exec('self.' + cmd)
        else:
            if ')' not in cmd: cmd += '()'
            print 'executing self.' + cmd
            try: 
                exec('self.res = self.' + cmd)
                if self.verbose > 0: self.view(self.res)
            except: pass
            
        
  
    def batch_vty(self):
        """
        help: perform command(s) on multiple hosts
        usage: 
        screen data will be wrote to self.out_file
        """
        
        try: cmd_list = self.cli_con.cmd_list
        except: return 'Enter a command with cmd='
        
        if len(self.batch_host_list) == 0: print 'No hosts are specified, search on host(s) and then enter batch add'
        
        for host in self.batch_host_list:
            
            try:    #do not try and connect if ping test fails
                if self.host_result[host] == 'fail': continue
            except: pass
            
            for cmd in cmd_list:
                try:
                   print 'command(s) to run %s \n' % cmd
                   self.batch_vty_go(host, cmd)
                
                except: print 'error with host %s cmd %s' % (host, cmd)
            
            
    def batch_vty_go(self, host, cmd):     
        self.vty_connect(ip='', host=host, cmd=cmd, verbose=1)
        if self.vty_out: 
            self.cli_con.post_session(self.vty_out, cmd, 1)
            self.list_to_file(self.vty_out, self.out_file, 'a')    #append mode
            time.sleep(self.time_wait)
            
            
    def views(self, q):
        """
        help: view class list, dictionary and variables
        usage:
        batch view ip
        batch view hosts
        batch view host_result
        batch view ping_dict
        batch view pent_hop
        batch view trace_dict
        batch view host_dict
        batch view dns_dict
        """
        if 'batch view ip' in q: q = 'batch view ip_list'
        if 'batch view hosts' in q: q = 'batch view batch_host_list'
        print 'self.view(' + 'self.' + q[11:] + ')'
        try: exec('self.view(' + 'self.' + q[11:] + ')')
        except: pass
    
    
    def com(self, q, view_list):
        """

        \n vty / tty    connect to vty on devices and run a command(s) and store screen output
        """
        self.view_list = view_list
        
        if 'batch in ' in q: self.remove_in_host_list(q[9:]) ; q = ''
        
        if 'batch not in ' in q: self.remove_not_in_host_list(q[13:]) ; q = ''
        
        if 'batch view ' in q: self.views(q) ; q = ''
        
        if 'batch set tcp port ' in q: self.set_tcp_port(q[19:]) ; q = ''
        
        
        if 'batch vty test arp ' in q: print self.vty_test_arp(q[19:]) ; q = ''
        
        if 'batch trans key test ' in q: print self.find_cmd_key(q[21:])
            
        if 'batch vty test cmd ' in q:
            ip = q.split(',')[1]
            cmd = q.split(',')[0][19:]
            print self.vty_test_cmd(ip, cmd) ; q = ''
        
        if 'batch vty sh ver ' in q: print self.vty_sh_ver(q[17:]) ; q = ''
        
        if 'vty' in q or 'tty' in q: return self.batch_vty()
        
        if 'batch test find arp' in q: print self.find_arp(q[20:])
        
        if 'batch ' in q: self.run(q[6:]) ; q = ''

            
