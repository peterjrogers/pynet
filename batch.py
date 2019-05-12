from tools import Tools
from mnet2 import Mnet
import time, os

class Batch(Tools, Mnet):
    def __init__(self, dev_con, cli_con):
        Tools.__init__(self)
        Mnet.__init__(self)
        
        """
        Batch processing tools
        
        (c) 2012, 2013 Intelligent Planet Ltd
        """
        
        self.path = os.getcwd() + '\\'
        self.clear()
        self.dev_con = dev_con
        self.cli_con = cli_con
        self.out_file = self.path + 'batch'
        self.time_wait = 1
        self.ttl = 35
        self.pent_hop = ''    #penultimate hop from the last traceroute performed
        self.batch_host_list = []    #hosts to perform the batch job on
        self.trace_dict = {}    #result of the traceroute
        self.ping_dict = {}
        self.host_dict = {}    #used for ip to hostname lookups
        self.vty_os = 'ios'
        
        #info obtained from sh ver in self.vty_sh_ver()
        self.init_sh_ver()
        
        #describe the output format for a command
        self.cmd_transform = {
            'sh ip arp': ['Protocol', 'Address', 'Age', 'Hardware Addr', 'Type', 'Interface'],
            'sh mac address-table': ['vlan', 'mac address', 'type', 'ports'],
            'sh mac add ': ['vlan', 'mac address', 'type', 'protocols', 'port'],
            'sh mac-add': ['star', 'vlan', 'mac address', 'type', 'learn', 'age', 'ports'],
            'sh int desc': ['interface', 'status', 'protocol', 'description'],
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
        Modify transform keys to make them specific to nexus NX-OS
        """
        self.cmd_transform['sh mac add '] = ['star', 'vlan', 'mac address', 'type', 'age', 'secure', 'ntfy', 'port']
        self.cmd_rules['sh mac add '] = ['dynamic', 3]
    
    def init_ios(self):
        """
        Modify transform keys to make them specific to IOS
        """
        self.cmd_transform['sh mac add '] = ['vlan', 'mac address', 'type', 'protocols', 'port']
        self.cmd_rules['sh mac add '] = ['dynamic', 3]
    
    
    def init_sh_ver(self):
        self.hostname = ''    
        self.serial_number = ''
        self.reload_cause = ''
        self.vty_os = 'ios'
    
    
    def clear(self): 
        self.batch_host_list = []
        
        
    def remove_in_host_list(self, txt): 
        res = [x for x in self.batch_host_list if txt in x]
        self.remove(res)
        
        
    def remove_not_in_host_list(self, txt): 
        res = [x for x in self.batch_host_list if txt not in x]
        self.remove(res)
        
        
    def list_format(self, clist):
        try: clist.sort()
        except: clist = [clist]
        finally: return clist
    
    
    def insert(self, view_list):
        
        view_list = self.list_format(view_list)
        
        for host in view_list:
            if host not in self.batch_host_list: 
                print 'added %s' % host
                self.batch_host_list.append(host)

                
    def remove(self, view_list):
        view_list = self.list_format(view_list)
        for host in view_list: self.pops(host) 
                  
            
    def pops(self, host):
        try:
            pos = self.batch_host_list.index(host)
            self.batch_host_list.pop(pos)
            print 'removed %s' % host
        except: print 'error removing %s' % host
        
        
    def make_ip_list(self):
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
        172.22.117.1 (1, 1, 2, 241, '172.22.117.1')
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
        
        
    def batch_ping(self): 
        self.make_ip_list()
        self.ping_dict = self.mt_ping(self.ip_list)
        self.process_ping(self.ping_dict)
        
        
    def view_ping_host_result(self): self.view(self.host_result)
    
    def view_ping_dict(self): self.view(self.ping_dict)
    
    def view_host_dict(self): self.view(self.host_dict)
        
        
    def batch_trace(self):
        """
        Run a multithreaded traceroute and store the result dict
        mt_trace output is {1: [(self.ping_sent, self.ping_recv, self.ping_delay, self.ping_ttl, hop_ip, host_name)]}
        """
        
        self.make_ip_list()
        
        for ip in self.ip_list:
            res = self.mt_trace(ip, ttl=self.ttl)
            if res:
                pent_index = len(res) - 1
                self.pent_hop = res[pent_index][0][4]
                self.trace_dict[ip] = {}
                self.trace_dict[ip]['output'] = res
                self.trace_dict[ip]['pent_hop'] = self.pent_hop
                
                
    def view_pent_hop(self): print self.pent_hop
    
    def view_trace_dict(self): self.view_pretty(self.trace_dict)
    
   
    def batch_rlook(self): 
        out = []
        self.make_ip_list()
        for ip in self.ip_list:
            print self.cli_con.verify_ip(ip)
        #return self.mt_dns_rlook(self.ip_list)
        
        
    def batch_port(self, q):
        self.make_ip_list()
        port = q.split()[-1]
        for ip in self.ip_list: 
            cmd = '%s:%s' % (ip, port)
            print 'trying port %s on %s' % (port, ip)
            self.cli_con.ping_tool(cmd)
            
            
    def find_ip(self, host):
        """
        Find the IP address via the device class passed into the batch class
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
        #port = self.find_port(ip, host)
        res = self.cli_con.test_session(host, ip)
        port = res[1]
        auth_type = res[0]
        
        time.sleep(self.time_wait)
        if verbose > 0: print 'batch vty connect', port, auth_type
        
        if auth_type != 'fail':
            self.vty_out = self.cli_con.vty_session(ip, host, port, cmd, auth_type)
            #Check if the vty output has been returned as a single entry list
            #if len(self.vty_out) == 1: self.vty_out = self.vty_out[0]
        
        
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
        Interface                      Status         Protocol Description
        
        """
        pass
        
        
    def vty_fixed_width_parse(self, ip, cmd):
        """
        Used a fixed width parse based on the label - i.e. as below
        Interface                      Status         Protocol Description
        get index positions of the heading words
        """
        pass
   
        
    def batch_vty(self):
        """
        perfrom command(s) on multiple hosts
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
    
    
    def com(self, q, view_list):
        """
        \n Batch commands
        \n help         display this help information
        \n add          add new hosts to the batch list
        \n add [host]   perfrom a whole or partial match against the db and add the matching hosts to the batch list
        \n clear        delete the batch list
        \n remove       remove host entry(s) from batch list
        \n view ip      view ip address list
        \n view host    view host list
        \n ping         perform a multithreaded ping on ip_list
        \n rlook        perfrom a multithreaded reverse dns lookup on ip_list
        \n port nn        perform a port check - i.e. batch port 23
        \n vty / tty    connect to vty on devices and run a command(s) and store screen output
        
        """
        if 'batch help' in q: return self.com.__doc__
        
        if 'batch add' in q:
            if len(q) > 9:
                res = q[9:].strip()
                view_list = self.dev_con.search_func(res)
            return self.insert(view_list)
        
        if 'batch remove' in q: 
            if len(q) > 12:
                res = q[12:].strip()
                view_list = self.dev_con.search_func(res)
            self.remove(view_list)
        
        if 'batch clear' in q: self.clear()
        
        if 'batch in ' in q: self.remove_in_host_list(q[9:]) ; q = ''
        
        if 'batch not in ' in q: self.remove_not_in_host_list(q[13:]) ; q = ''
        
        if 'batch view' in q:
            if 'ip' in q: 
                self.make_ip_list()
                self.view(self.ip_list)
            
            if 'ping_host_result' in q: self.view_ping_host_result() ; q = ''
            
            if 'ping_dict' in q: self.view_ping_dict() ; q = ''
            
            if 'pent_hop' in q: self.view_pent_hop()
            
            if 'trace_dict' in q: self.view_trace_dict()
            
            if 'host_dict' in q: self.view_host_dict() ; q = ''
            
            if 'host' in q: self.view(self.batch_host_list)
              
            q = ''
                 
            
        if 'batch ping' in q: self.batch_ping()
        
        if 'batch trace' in q: self.batch_trace()
        
        if 'batch rlook' in q: return self.batch_rlook()
        
        if 'batch port' in q: return self.batch_port(q)
        
        if 'batch vty test arp ' in q: print self.vty_test_arp(q[19:]) ; q = ''
        
        if 'batch trans key test ' in q: print self.find_cmd_key(q[21:])
            
        if 'batch vty test cmd ' in q:
            ip = q.split(',')[1]
            cmd = q.split(',')[0][19:]
            print self.vty_test_cmd(ip, cmd) ; q = ''
        
        if 'batch vty sh ver ' in q: print self.vty_sh_ver(q[17:]) ; q = ''
        
        if 'vty' in q or 'tty' in q: return self.batch_vty()
        
        if 'batch test find arp' in q: print self.find_arp(q[20:])
        
        
            
