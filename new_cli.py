import sys, time, macs, device2, contact, mac, cache_flow, arps, ports2, pynet, auth, re
import net2, os, mnet2, vty2, session3, batch, ipcalc, pyputty, shutil, getpass
from subprocess import Popen, PIPE
from tools import Tools
try: 
    import pygeoip
    path = os.getcwd() + '\\'
    cfile = path + 'GeoLiteCity.dat'
    gi = pygeoip.GeoIP(cfile)
except: pass

mac_con = macs.Macs()
dev_con = device2.Device()
contact_con = contact.Contact()
mac_oui = mac.Mac()
cache_con = cache_flow.Cache_flow()
ports_con = ports2.Ports()
mnet_con = mnet2.Mnet()
net_con = net2.Net()
auth_con = auth.Auth()
auth_con.auth_enable()    #load the enable password


decrypt=lambda x:''.join([chr(int(x[i:i+2],16)^ord('dsfd;kfoA,.iyewrkldJKDHSUBsgvca69834ncxv9873254k;fg87'[(int(x[:2])+i/2-1)%53]))for i in range(2,len(x),2)])    #http://packetstormsecurity.com/files/author/7338/


class Cli(Tools):
    def __init__(self):
        Tools.__init__(self)
        
        """
        Search interface for host, ip  and extended information within device db
        Start point for Command line networking toolkit
        
        Tested with Python ver 2.7.2 on Win7 & Win XP
        (c) 2012 - 2014 Intelligent Planet Ltd        
        """
        
        self.verbose = 0
        
        ### cli vars ###
        self.search_txt = '\n\nsearch >>>'
        self.user = getpass.getuser()
        
        ### set the path to csv device files ###
        try: 
            self.path = 'H:/crt/sessions/'
            cfile = self.path + 'telnet.ini'
            open(cfile)
        except: 
            try: 
                self.path = 'C:/Documents and Settings/' + self.user + '/Application Data/VanDyke/SecureCRT/Config/sessions/'
                cfile = self.path + 'telnet.ini'
                open(cfile)
            except: self.path = os.getcwd() + '\\'
        
        self.log_file = os.getcwd() + '\\' + 'log'
        self.sticky = 1    #can be set to 0 to disable level1 cli
        self.session_fail_delay = 2
        self.session_start_delay = 1
        self.total_records = len(dev_con.search_db)
        self.total_hosts = len(dev_con.index)
        self.batch_con = batch.Batch(dev_con, self)
        self.host_list = []
        self.dns_suffix = []
        
        self.test_dns_suffix()
        self.arp_start()
        self.level_0()
        

    def level_0(self):
        """
        Top level function
        
        To exit from this level closes the cli app
        
        Search by host, ip, model, serial, mac, town, postcode etc
        
        ?            Display multiple matching host records\n
        @            Open a pre made session e.g. @ba\n
        %name,ip     Open ad-hoc session e.g. %Router1,10.1.1.1\n
        sticky 0     Disables level 1 CLI for cut & paste searches    sticky re-enables
        batch [help]    perform batch operations
        
        http    get data with http(s) direct
        prohttp   get data with http(s) via proxy server
        
        ehealth [url user pass]   run a custom analysis of an ehealth report
        ehealth internet   run Peter Ortlepp's internet report 

        """
        print "%s records loaded for %s devices" % (self.total_records, self.total_hosts)
        
        out = []
        view_list = []
        
        while True:
            res = raw_input(self.search_txt)
            start = time.time()
            res_copy = res.rstrip('\n')
            res = res.rstrip('\n').lower()

            if res:
            
                if res == 'exit': return    #exit the program
           
                if res == 'help':    #print the module docstring
                    print self.level_0.__doc__
                    print self.level_7.__doc__    #common tools
                    res = ''
               
                if res == '?':    #print each item in the view_list
                    try: 
                        for item in view_list: print item.upper()
                    except: pass
                    res = ''

                if '@' in res:    #open a previously made session file by file name
                    self.pre_session(res)
                    res = ''

                if '%' in res:    #open a new ad-hoc session - format is %hostname,ip_address
                    try:
                        raw = res[1:].split(',')
                        self.crt_session(raw[0], raw[1])
                    except: pass
                    res = ''
                    
                if 'sticky ' in res:    #disable level1 interface for copy / paste searches
                    if '0' in res: self.sticky = 0
                    else: self.sticky = 1
                    res = ''
                    
                if 'batch ' in res:    #perform batch operations - use batch help for extended help
                    #try:
                        batch_out = self.batch_con.com(res, self.host_list)
                        if batch_out: print batch_out
                    #except type: pass
                    #finally: res = ''
                        res = ''
                    
                if 'whois ' in res:
                    try:
                        url = 'http://www.whois.com/whois/' + res[6:]
                        print url
                        http_data = net_con.get_http_proxy(url)[3]
                        #print http_data
                        self.viewwhois(http_data)
                        ip_string = res[6:]
                        print '\nRule to block this host on RT03PBLYINET01\nip route %s 255.255.255.255 192.0.2.1 tag 666' % ip_string
                        send = 'echo %s| clip' % auth_con.enable_password
                        self.send_clip(send)
                    except: pass
                    finally: res = ''
                    
                    
                if 'ehealth ' in res:    #run an ehealth report conversion
                    if 'internet' in res:    #fetch the data for Peter Ortlepp's report
                        url = 'http://22.98.33.26/users/guest/myHealth/myHealth.csv'
                        username = 'guest'
                        password = 'guest'
                    else: 
                        ehealth_split = res_copy.split(' ')    #keep the char case
                        if len(ehealth_split) != 4: 
                            print '\n *** error *** command format is [ehealth url user pass]\n'
                            res = ''
                        if len(ehealth_split) == 4:
                            url = ehealth_split[1]
                            username = ehealth_split[2]
                            password = ehealth_split[3]
                            res_copy = ''
                        
                    if res:
                        print '\n getting the data from ehealth server with url -', url
                        http_data = net_con.get_http_auth(url, username, password)
                        path = os.getcwd() + '\\'
                        eheath_file = path + 'myHealth.csv'
                        out_file = open(eheath_file, 'w')
                        try:
                            for line in http_data.read(): out_file.write(line)
                        except: pass
                        out_file.close()
                        print '%s file written' % eheath_file
                        
                        try: reload(ehealth)
                        except: 
                            try: from pynet import ehealth
                            except: pass
                    
                        finally: res = ''
                        
                
                if 'http' in res:    #get data via http
                    try:
                        if 'prohttp' in res: http_data = net_con.get_http_proxy(res[3:])
                        else: http_data = net_con.get_http(res)
                        self.view_http(http_data[3])
                        print 'status code %d    status msg %s    url %s' % (http_data[0], http_data[1], http_data[2])
                    except: pass
                    finally: res = ''
                    
                res = self.level_7(res)    #check macthing commands in the common tools
                
                if res:    
                    """
                    If res did not match a command then perform a host search and return
                    a view_list if more than on host matches.
                    The view_list can then be used to specify batch host targets
                    """                    
                    view_list = self.host_search(res)
                    res = ''
                    
                
                    
    def level_1(self, hostname, ip_address, port, auth):
        """
        Command line session function
        Perform actions on the selected device
        
        info          Display info records
        
        vty / tty     Open vty session to device
        http(s)       Open http ot https session to device
        
        %command      Run a single command on the device - e.g. %sh int desc
        cmd=a,b       Create a list of multiple commands to run - e.g. cmd=sh arp,sh int desc
        @cmd          Run multiple commands from list created with cmd=a,b
        
        ip=x.x.x.x    Change the session IP address
        +1 or -1       Increase / decrease the session IP adress by 1
        
        @arp           Command macro runs sh ip arp and then analyses output\n
        @x25           Command macro runs sh x25 route  sh x25 vc | inc Interface|Started|Connects\n
        @int           Command macro runs sh int desc  sh ip int brief  sh int count err  sh ip arp
                       sh ip bgp sum  sh ip route sum  sh ver | inc uptime|System|reason|cessor  
                       sh standby | inc Group|State|change|Priority\n
        @bip           Command macro runs sh ip bgp sum | beg Neigh, sh controller vdsl 0/0/0 | inc dB|Speed|Reed|Err 
                          and sh controller vdsl 0/1/0 | inc dB|Speed|Reed|Err\n
        @cache        Command macro runs sh ip cache flow and reformats the output to show protocol names
                          well know port names and decimal port numbers, also it displays in accending packet order\n
        @mac         Command macro runs sh mac-add dyn and enters the values into a searchable mac db\n
        @nex_mac        Command macro as @mac but for use on nexus switches\n
        @x25        Command macro runs x25 commands\n
        @cpu        Command macro runs cpu related command on a switch\n
        @int        Command macro runs interface information commands\n
                       
        q              Exit session mode and return to search mode
        """
        
        c = 1
        while 1:
            print '\n%s >>>' % (hostname.upper()),
            
            q = raw_input()
            q = q.lower()
            
            if '@arp' in q: q = '%sh ip arp'
            
            if '@bip' in q: self.cmd_list = ['sh ip bgp sum | beg Neigh', 'sh controller vdsl 0/0/0 | inc dB|Speed|Reed|Err', 'sh controller vdsl 0/1/0 | inc dB|Speed|Reed|Err'] ; q = '@cmd'
            
            if '@mac' in q: q = '%sh mac-add dyn'
            
            if '@cache' in q: q = '%sh ip cache flow'
            
            if '@nex_mac' in q: q = '%sh mac address-table dynamic'
            
            if '@x25' in q: self.cmd_list = ['sh x25 rou','sh x25 vc | inc Interface|Started|Connects'] ; q = '@cmd'
            
            if '@cpu' in q: self.cmd_list = ['sh proc cpu sort | exc 0.00', 'sh proc cpu his', 'sh plat health', 'sh plat cpu packet stat all'] ; q = '@cmd'
            
            if '@int' in q: self.cmd_list = ['sh int desc','sh ip int brief','sh int count err','sh ip arp','sh ip bgp sum','sh ip route sum','sh ver | inc uptime|System|reason|cessor','sh standby | inc Group|State|change|Priority'] ; q = '@cmd'

            if 'ping' in q and len(q) == 4: q = 'ping %s' % ip_address ; c +=1

            if 'trace' in q: q = 'trace %s' % ip_address ; c +=1
            
            if 'scan' in q: q = 'scan %s' % ip_address ; c +=1
        
            if 'http' in q: self.start_http(q, ip_address) ; c +=1
            
            if 'info' in q: dev_con.show_info(hostname) ; c +=1
                
            if 'ip=' in q: ip_address = q[3:] ; c +=1
            
            if '+1' in q: 
                ip_address = self.ip_add(ip_address)
                print 'ip', ip_address ; c +=1
                
            if '-1' in q: 
                ip_address = self.ip_sub(ip_address)
                print 'ip', ip_address ; c +=1
            
            if 'help' in q: 
                print self.level_7.__doc__    #common tools
                print self.level_1.__doc__ ; c +=1
                
            if '@cmd' in q:
                self.open_vty(hostname, ip_address, port, auth, cmd=self.cmd_list, type='internal')
                #res = self.test_session(hostname, ip_address)
                #print res
                #example of res - ('bt', 22)
                #if res[0] != 'fail': 
                #    raw = self.py_session(ip_address, hostname, res[1], self.cmd_list, res[0])
                q = '' ; c +=1
                
            if 'vty' in q or 'tty' in q: 
                self.open_vty(hostname, ip_address, port, auth, cmd='', type='putty')
                #self.vty_method(hostname, ip_address)
                c +=1
                
            if 'search' in q or 'q' in q or 'exit' in q: return
            
            if '@' in q: self.pre_session(q) ; c += 1
                        
            if 'sh ' in q[0:3] or 'show ' in q[0:5]: q = '%' + q
            
            if '%' in q: 
                cmd=q[1:]
                self.open_vty(hostname, ip_address, port, auth, cmd, type='internal')
                #res = self.test_session(hostname, ip_address)
                #print res
                #example of res - ('bt', 22)
                #if res[0] != 'fail': 
                #    raw = self.py_session(ip_address, hostname, res[1], q[1:], res[0])
                q = '' ; c +=1
                
            q = self.level_7(q)    #check matching commands in the common tools
                
            try: 
                ### delete stored TACACS password if not logged in using same user id
                if auth_con.tacacs_user != self.user: auth_con.tacacs_password = ''
            except: pass
            
            c -= 1
            
            if c < 0: return
             

    def level_7(self, res):
        """
        arp [ip mac hostname]    Display arp records\n
        runarp    load arp report from a manually loaded source file (R++)\n
        mac [mac]    Display mac records\n
        name        Display contact db records\n
        oui [mac]  Display MAC OUI info\n
        ports [# / name]  Display well known port info - search by port #, name or desc\n
        ping x.x.x.x [:port]  Ping MAC, Nmae, IP / Port with DNS, Reverse DNS, ARP & Db lookup\n
        trace [ip]    Traceroute\n
        scan [ip]    Port scanner\n
        rlook [ip]    Reverse name lookup\n
        look[host name]    name lookup\n
        decrypt [cisco level 5 encrypted password]    cisco password decoder\n
        cidr [ip/bits]      Subnet calculator\n
        geoip x.x.x.x    GeoIP info\n
        whois x.x.x.x    Perform a whois lookup on an internet address\n
        send x.x.x.x     send a string to a TCP port with - send 10.7.9.201 80 get\n
        telnet / ssh x.x.x.x    connect to host by ip or domin name\n
        """
        
        if 'cmd=' in res: 
            self.cmd_list = res[4:].split(',')
            print self.cmd_list ; res = ''
        
        if 'runarp' in res:    #load arp report from a manually loaded source file
            try:
                self.arp_start()
                self.arp_con.arp_go()
                self.arp_con.save_report()
            except: print 'error'
            finally: res = ''
        
        if 'arp ' in res:    #perform a search of the historic arp db
            try: self.arp_search(res[4:])
            except: pass
            res = ''
                
        if 'mac ' in res:    #perform a search of the historic mac db
            self.mac_search(res[4:])
            res = ''

        if 'name ' in res:    #perform a search of the contact db
            contact_con.search_func(res[5:])
            res = ''
            
        if 'oui ' in res:    #perform a OUI mac vendor lookup
            print mac_oui.id_mac(res[4:])
            res = ''
            
        if 'ports ' in res:    #perform a well know port lookup
            ports_con.find_port(res[6:])
            res = ''
            
        if 'pings alert' in res:
            self.ping_alert()
            res = ''
            
        if 'ping ' in res:    #perform a ping or port ping test by specifying the ip address and port if required
            self.ping_tool(res[5:])
            res = ''

        if 'pings ' in res:
            res_list = res[5:].split()
            for item in res_list: self.ping_tool(item.strip(','))
            res = ''
            
        if 'send ' in res:    #send a string to a TCP port with - send 10.7.9.201 80 get
            try:
                sres = res[5:].split(' ')
                end = len(sres[0]) + len(sres[1]) + 7    #starting point of the command
                print net_con.test_port(int(sres[1]), sres[0], res[end:].strip("'"))
            except: pass
            finally: res = ''
            
        if 'trace ' in res:    #perform a traceroute
            try:
                test = self.verify_ip(res[6:])
                if test: 
                    out = mnet_con.mt_trace(test[0], 35)
            except: pass
            finally: res = ''
            
        if 'scan ' in res:    #perfrom a port scan
            try:
                test = self.verify_ip(res[5:])
                if test:
                    self.view(net_con.scan(test[0]))
            except: pass
            finally: res = ''
            
        if 'look ' in res:    #perfrom a reverse lookup
            con = net2.Net()
            try:
                if 'rlook' in res: print con.dns_rlook(res[6:])
                else: 
                    out = con.dns_look(res[5:])
                    print out, con.dns_rlook(out)
            except: pass
            finally: res = ''
            
        if 'decrypt ' in res:    #cisco type 7 password decode
            print decrypt(res[8:])
            res = ''
            
        if 'cidr ' in res:    #cidr calculator
            try: 
                net = ipcalc.Network(res[5:])
                print ' Network:     %s\n First host:  %s\n Last host:   %s\n Broadcast:   %s\n Netmask:     %s\n Num Hosts:   %s\n' % (net.network(), net.host_first(), net.host_last(), net.broadcast(), net.netmask(), str(net.size()-2))
            except: pass
            finally: res = ''
            
        if 'geoip ' in res:    #Internet GeIP lookup
            try:
                out = gi.record_by_addr(res[6:])
                self.view(out)
            except: pass
            finally: res = ''
            
        if 'telnet ' in res:
            try: 
                ip_address = res[7:]
                t_path = os.getcwd() +'\\'
                t_cmd = '%sputty -telnet %s' % (t_path, ip_address)
                Popen(t_cmd)
            except: pass
            finally: res = ''
            
        if 'ssh ' in res:
            try: 
                ip_address = res[4:]
                t_path = os.getcwd() +'\\'
                t_cmd = '%sputty -ssh %s' % (t_path, ip_address)
                Popen(t_cmd)
            except: pass
            finally: res = ''
            
        if 'tty ' in res or 'vty ' in res:
            try: 
                ip_address = res[4:]
                self.vty_method(ip_address, ip_address)
            except: pass
            finally: res = ''
            
        return res    #returns the original string if no match          
        
        
    def test_dns_suffix(self):
        if not self.dns_suffix:
            cfile = os.getcwd() + '\\' + 'dns_suffix'
            rfile = open(cfile, 'rU')
            for row in rfile:
                if row: 
                    suffix = row.strip('\n').rstrip().lstrip()
                    if suffix not in self.dns_suffix: self.dns_suffix.append(suffix)
            #print self.dns_suffix
            
    
    def search_db(self, q):
        res = dev_con.search_func(q, 1)
        self.host_list = dev_con.host_list
        if len(self.host_list) == 1: return dev_con.ip, dev_con.host
        
    
    def verify_ip(self, ip):
        #test if ip or host name
        con = net2.Net()
        res = ip.split('.')
        
        if len(res) == 4:
            try: 
                for item in res: int(item)
                #valid IP detected
                #perfrom a db lookup
                res = self.search_db(ip)
                if res: return ip, res[1]    #db search produced a unique match
                
                return ip, con.dns_rlook(ip)
            except: return ip, ip
        
        print 'trying to resolve name %s\n' % ip
        
        if len(res) > 1:
            #resolve host name using normal dns lookup with a reverse lookup to varify FQDN
            try: 
                rtn_ip = con.dns_look(ip)
                return rtn_ip, con.dns_rlook(rtn_ip)
            except: pass
        
            #resolve host name using normal dns lookup without reverse lookup
            try: return con.dns_look(ip), ip
            except: pass
        
        #resolve host name using dns suffix list
        res = con.dns_look_suffix(ip, self.dns_suffix)
        if res: 
            print 'match on FQDN: %s\n' % res[1]
            try: return res[0], con.dns_rlook(res[0])
            except: return res[0], res[0]
            
        #perfrom a db lookup
        res = self.search_db(ip)
        if res: return res    #db search produced a unique match
        
        #perform an arp lookup
        res = self.arp_con.search_ip(ip)
        if res: 
            print 'matching ARP record'
            self.arp_search(ip)
            ip_res = res[2].split('_')[0]
            return ip_res, ip_res
        
    def vty_method(self, hostname, ip_address):
        #open a connection via an external client - SecureCRT or Putty
        if hostname == ip_address:
            res = self.verify_ip(ip_address)
            if res:
                ip_address = res[0]
                hostname = res[1]
        
        #test the auth type for putty
        test = self.test_session(hostname, ip_address)
        if test[0] != 'fail':
            port = test[1]
            auth_type = test[0]
            print 'connecting via external client', hostname, ip_address, port, auth_type
            try: self.crt_session(hostname, ip_address)
            except: pyputty.Putty(ip_address, hostname, port, auth_type)
            
        return 'failed to test connection to', ip_address
          
    
    def pre_session(self, res):    
        """
        Start pre made session from  self.path\Sessions\
        Use the launch function in session3.py with an empty connection_type
        Pass in the self.path value to keep it working with custom secure crt implementations
        """
        if len(res) > 1:
            ses_con = session3.SecureCRT(res[1:], '0.0.0.0', self.path)
            ses_con.launch()
            
            
    def crt_session(self, hostname, ip):
        """
        Make a session for SecureCRT and launch a new CRT window
        """
        ses_con = session3.SecureCRT(hostname, ip, self.path)
        ses_con.make()
        ses_con.launch()
        
        
    def test_session(self, hostname, ip):
        """
        Test the connection type and authentication
        """
        ses_con = session3.SecureCRT(hostname, ip, self.path)
        return ses_con.test(), ses_con.port
        
        
    def open_vty(self, hostname, ip, port, auth, cmd, type='internal'):
        """
        New method to open a direct vty connection.
        1) if port is not passed in then test for ssh then telnet
        2) if auth method is not passed in then test against know names
       """
        if not port:
            con = net2.Net()
            
            #test for ssh
            port = 22
            res = con.test_port(port, ip)
            if 'fail' in res[0]:
                #ssh must have failed so try telnet
                port = 23
                res = con.test_port(port, ip)
                if 'fail' in res[0]:
                    print 'unable to connect with either ssh or telnet'
                    #add a logging file for failed connections#
                    return 'fail'
                    
        #test for auth
        if not auth:
            bt_host = ['bip-', 'san-b', 'san-h', 'san-t', 'ab-h', 'san-d', 'ab-bbg', 'alg-1004', 'alg-1002', 'alg-1003', 'alg-1004', 'alg-1005', 'alg-1009', 'alg-101']
            for item in bt_host:
                if item in self.hostname.lower(): auth='bt'
            #if auth was not matched by the bt_host list then default to produban
            if not auth: auth='produban'
             
        #open the connection
        if type == 'putty': pyputty.Putty(ip, hostname, port, auth)
        if type == 'internal': self.py_session(ip, hostname, port, cmd, auth)
         
            
            
    

    def arp_start(self):
        self.arp_con = arps.Arp()
        
        
    def arp_search(self, res):
        """
        Search, display and maintain historical arp records
        """
        key_fail = self.arp_con.display_by_key(res)
        if not key_fail: return    #matched on a key so do not proceed to other functions
        
        if 'keys' in res:
            self.arp_con.list_keys()
            return
            
        if 'delete' in res:
            self.arp_con.delete_key(res[7:])
            return
        
        db_keys = self.arp_con.search_ip(res)
        if db_keys:
            self.arp_con.display_key_int_mac(db_keys[0], db_keys[1], db_keys[2])    #key, interface, ip_mac
            self.arp_con.display_record(db_keys[0], db_keys[1], db_keys[2])    #key, interface, ip_mac
        else: self.arp_con.search_ip(res, 1)    #like = 1
        
        """
        if res: 
            view_list = self.arp_con.search_mac(res)
            if len(view_list) == 1: 
                res = view_list[0].split('_')
                ip_address = res[0]
                hostname = res[1]
                print '\n Matched in ARP db  %s    %s\n' % (ip_address, hostname)
                self.arp_con.view_records(ip_address)
                self.level_1(hostname, ip_address)
            else:
                for item in view_list: print 'ARP db    ',item
        """
        
    def mac_search(self, res):
        """
        Search and display historical mac records
        """
        if res: self.view(mac_con.search(res))
               
            
    def host_search(self, q):
        """
        Search and display host devices and goto level_1 if a single matching entry is found
        """
        if q:
            res = dev_con.search_func(q)
            self.host_list = dev_con.host_list
            if len(res) == 1 and self.sticky ==1:
                self.ip_address = dev_con.ip
                self.hostname = dev_con.host
                self.auth = dev_con.auth
                self.port = dev_con.port
                self.level_1(self.hostname, self.ip_address, self.port, self.auth)
                
            else: return res    #return the list so it can be used for batch work
                
                
    def ping_tool(self, res):
        try:
        
            if res:
                if ':' in res:
                    raw = res.split(':')
                    ip_address = raw[0].lstrip().rstrip()
                    port = raw[1]
                else: 
                    ip_address = res.lstrip().rstrip()
                    port = ''
                
                #perfrom db or dns lookup
                test = self.verify_ip(ip_address)
                if test: 
                    ip_address = test[0]
                    name = test[1]
                    print 'Resolves to IP: %s\n\nReverse lookup of %s: %s\n' % (ip_address, ip_address, name)
                else: 
                    print 'unable to resolve %s' % ip_address
                    return
                
                con = net2.Net(ip_address, 'ping_test')
                if port:
                    if ':80' in res: print con.test_http(80, ip_address)
                    else: print con.test_port(int(port), ip_address)
                    time.sleep(1)
                
                else: con.ping(ip_address)
        except: print 'error'
        
        
    def ping_alert(self):
        """
        Read the alert from alert.txt and split the below line to extract the FQDN
        [Ping failed on txlara.santanderuk.gs.corp,
        """
        con = net2.Net()
        cfile = os.getcwd() + '\\' + 'alert.txt'
        lines = open(cfile, 'rU')
        for line in lines:
            if 'Ping failed' in line:
                ip = line.split()[3].strip(',')
                print '\n', con.test_ping(ip)
            
            
    def start_http(self, protocol, url):
        ##### start "" "http://bbc.co.uk" #####
        cmd = 'start %s://%s' % (protocol, url)
        os.system(cmd)   
    
              
    def py_session(self, ip, host, port, cmd, auth_type):
        try:
            out = self.vty_session(ip, host, port, cmd, auth_type)
            return self.post_session(out, cmd)
        except: print 'failed'
    
    
    def vty_session(self, ip, host, port, cmd, auth_type):
        print 'command(s) to run', cmd
        con = vty2.Vty(ip, host, port, auth_type)
        con.verbose = 1
        self.session_try = 0
        
        time.sleep(self.session_start_delay)    #wait to ensure that test port closed down
        
        while self.session_try < 1:
        
            if port == 23:
                res = con.telnet_go(cmd)
                if res:  print res; self.session_fail()
                else: return con.telnet_out

            if port == 22:
                res = con.ssh_go(cmd)
                if res: print res; self.session_fail()
                else: return con.ssh_out
                
        return ''

            
    def session_fail(self):
        try:
            print 'attempt %d failed' % self.session_try
            self.session_try += 1
            time.sleep(self.session_fail_delay)
        except: pass
            
        
    def post_session(self, out, cmd, silent=0):
        self.view(out)
        
        if out:
            if 'arp' in cmd: 
                try:
                    self.list_to_file(out, self.arp_con.cfile)
                    self.arp_start()
                    self.arp_con.arp_go()
                    if silent < 1: self.arp_con.save_report()
                except: pass
                
            if 'mac' in cmd: 
                self.list_to_file(out, mac_con.load_file)
                mac_con.load()
                mac_con.save()
                
            if 'cache' in cmd:
                self.list_to_file(out, cache_con.load_file)
                cache_con.test()
                
            if 'sh ip int brief' in cmd:
                #example of output
                #san-b0170-rtr-01#sh ip int brief
                #Vlan10                     10.180.200.114  YES NVRAM  up                    up
                
                hostname = 'hostname error'
                cfile = os.getcwd() + '\\' + 'out.txt'
                print 'outputing ip interface data to', cfile
                
                if len(out) == 1: out = out[0]
                
                for row in out:
                    try: 
                        #Strip out the telnet chars that appear after more - \x08\x08\x08\x08\x08\x08\x08\x08\x08
                        m = re.search('[A-Za-z].*$', row)
                        if m: row = m.group()
                        
                        #capture the device hostname
                        if '#sh ip int brief' in row: hostname = row.split('#')[0].strip()
                        if '>sh ip int brief' in row: hostname = row.split('>')[0].strip()
                    
                        #check for an ip address in the row
                        if '.' in row.split()[1]:
                            interface = row.split()[0]
                            ip = row.split()[1]
                            line = '%s,%s,%s\n' % (hostname, interface, ip)
                            print line
                            self.write_line_to_file(line, cfile)
                    
                    except: print 'error on row', row
                    
                    
            if 'sh ip route' in cmd:
                #example of output
                #san-b0617-rtr-01#sh ip route conn
                #C        10.67.32.224/28 is directly connected, Vlan201
                
                hostname = 'hostname error'
                cfile = os.getcwd() + '\\' + 'out.txt'
                print 'outputing ip interface data to', cfile
                
                if len(out) == 1: out = out[0]
                
                for row in out:
                    try: 
                        #Strip out the telnet chars that appear after more - \x08\x08\x08\x08\x08\x08\x08\x08\x08
                        m = re.search('[A-Za-z].*$', row)
                        if m: row = m.group()
                        
                        #capture the device hostname
                        if '#sh ip route' in row: hostname = row.split('#')[0].strip()
                        if '>sh ip route' in row: hostname = row.split('>')[0].strip()
                    
                        #check for an ip address in the row
                        if '.' in row.split()[1]:
                            protocol = row.split()[0]
                            ip = row.split()[1]
                            metric = row.split()[2]
                            if 'is' in metric: metric = '[0/0]'
                            via = row.split()[4].strip(',')
                            interface = row.split()[5]
                            line = '%s,%s,%s,%s,%s,%s\n' % (hostname, protocol, ip, metric, via, interface)
                            print line
                            self.write_line_to_file(line, cfile)
                    
                    except: print 'error on row', row
                
            #Log vty output to the main log file.
            self.list_to_file(out, self.log_file, 'a')
                
        return out
                  
       
def go():
    x = Cli()
    
    
if __name__ == "__main__":
    go()     
