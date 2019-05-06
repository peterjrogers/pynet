from tools import Tools
import os

class Batch(Tools):
    def __init__(self, cmd, vty_output, vty_os='ios'):
        Tools.__init__(self)
        
        """
        CLI Parsing tools
        This class is designed to read the output from Cisco CLI commands and return it as recognised data elements
        
        Example of the usage:
        cmd='sh ip arp'        
        
        vty_output is the vty session output that is being passed into this class (as per the below example)
        R7#sh ip arp
        Protocol  Address          Age (min)  Hardware Addr   Type   Interface
        Internet  10.10.10.29            19   ca05.0694.0000  ARPA   FastEthernet0/0

        vty_os = 'ios'
        if the operating system is not known then pass the sh ver ourput into vty_output and run self.vty_sh_ver()
        
        call the parsing function with self.vty_parse(cmd='sh ip arp', verbose=1)
        
        (c) 2012 - 2019 Intelligent Planet Ltd
        """
        
        self.path = os.getcwd() + '\\'
        
        #there are 3 possible inputs for this module
        self.vty_out = vty_output 
        self.cmd = cmd
        self.vty_os = vty_os
        
        #set the transform keys for the correct cisco os
        #
        self.vty_set_transform(self.vty_os)
        
        
        #describe the output format for a command
        self.cmd_transform = {
            'sh ip arp': ['Protocol', 'Address', 'Age', 'Hardware Addr', 'Type', 'Interface'],
            'sh mac address-table': ['vlan', 'mac address', 'type', 'ports'],
            'sh mac add ': ['vlan', 'mac address', 'type', 'protocols', 'port'],
            'sh mac-add': ['star', 'vlan', 'mac address', 'type', 'learn', 'age', 'ports'],
            'sh int desc': ['interface', 'status', 'protocol', 'description'],
            'sh ver': ['hostname', 'serial_number', 'reload_cause'],
            'sh ip int brief': ['interface', 'ip', 'ok', 'method', 'status', 'protocol']
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
            'nxos': ['device name', 2, 'processor', 3, 'reason:', 1],
            'sh ip int brief': ['interface', 0, 'ip-address', 1, 'ok?', 2]
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
        
        
    def find_cmd_key(self, cmd):
        """
        Step through the cmd one char at a time until a unique cmd_transform key match is found
        batch trans key test sh mac address-table address 000b.5de3.7ee6
        """
        for pos in range(4, len(cmd)):
            key = [x for x in self.cmd_transform.keys() if cmd[:pos] in x]
            if len(key) == 1: return key[0]
        
        
    def vty_parse(self, cmd='', verbose=1):
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
        
        
    def vty_sh_ver(self):
       """
       vty.out should include the sh ver output
       
       """
       
       self.init_sh_ver()
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
        
        
    def vty_fixed_width_parse(self, ip, cmd):
        """
        Used a fixed width parse based on the label - i.e. as below
        Interface                      Status         Protocol Description
        get index positions of the heading words
        """
        pass
   
        
