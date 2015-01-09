import socket, re, time, urllib2, base64
from subprocess import Popen, PIPE
from tools import Tools

class Net(Tools):
    def __init__(self, ip='192.168.1.10', name='test', port=23):
        Tools.__init__(self)
        """
        Network tool kit
        Tested on Win XP with Python 2.7
        (c) 2012 - 2014 Intelligent Planet Ltd
        """
        
        self.init_net(ip, name, port)
               
        self.timeout = 0.2
        self.sleep = 0.1
        self.verbose = 1
       
        self.buffers = 1024
        self.error = 'fail'
        
        self.web_proxy = '172.19.193.122'
       
        self.port_list = [20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 161, 162, 179, 443, 520, 1719, 1720, 1985, 1998, 2000, 2427, 3389, 5060, 5900, 8080]
        #FTP(20, 21), SSH(22), Telnet(23), SMTP(25), DNS(53), DHCP(67, 68), TFTP(69), HTTP(80), SNMP(161, 162), BGP(179), HTTPS(443), RIP(520)
        #H.323(1719. 1720), HSRP(1985), XOT(1998), SCCP(2000), MGCP(2427), RDP(3389), SIP(5060), VNC(5900)
       
        self.http_get = 'GET /index.html HTTP/1.1 \r\n'
        self.http_host = 'Host: %s \r\n\r\n'
        
        
    def init_net(self, ip, name, port):
        self.ip = ip
        self.host_name = name
        self.port = port
       
       
    def socket_open(self, port, ip):
        try:
            self.sock = socket.socket()
            self.sock.settimeout(self.timeout)
            self.sock.connect((ip, port))
        except socket.error, e: return (self.error, 'socket_open', e)
       
       
    def socket_close(self):
        try: self.sock.close()
        except: pass
       
       
    def socket_peer_name(self):
        try: return self.sock.getpeername()
        except socket.error, e: return (self.error, 'socket_peer_name', e)
       
       
    def socket_recv(self):
        try: return self.sock.recv(self.buffers)
        except socket.error, e: return (self.error, 'socket_recv', e)
       
       
    def socket_send(self, data):
        try: self.sock_sent_bytes = self.sock.send(data)
        except socket.error, e: return (self.error, 'socket_send', e)
       
       
    def test_http(self, port, ip):
        error = self.socket_open(port, ip)
        if error: return error
        self.socket_send(self.http_get)
        self.socket_send(self.http_host % (self.ip))
        return self.socket_recv()
       
       
    def test_port(self, port, ip, send=''):
        """
        help: tcp port test, will open a session to the host / port and return any received data
        usage: test_port(port, ip, send)    #send is optional
        example: test_port(80, '4.4.4.4')
        """
        error = self.socket_open(port, ip)
        if error: return error
        time.sleep(self.sleep)
        if send:
            self.socket_send(send)
            time.sleep(self.sleep)  
        return self.socket_recv()
        
        
    def test_port_front(self, port, ip, send=''):
        if port == 80: print 'http test' ; return self.test_http(port, ip)
        return self.test_port(port, ip)
       
       
    def test_ping(self, ip, ttl=255, count=1, timeout=300, size=32):
        cmd = "p = Popen('ping -n %s -w %s -i %s -l %s %s', stdout=PIPE)" % (count, timeout, ttl, size, ip)
        exec(cmd)
        
        self.ping_result = p.stdout.read()
       
        m = re.search('Sent = ([0-9]+),', self.ping_result)
        if m: self.ping_sent = int(m.group(1))
        
        m = re.search('Received = ([0-9]+),', self.ping_result)
        if m: self.ping_recv = int(m.group(1))
        
        m = re.search('TTL=([0-9]+)', self.ping_result)
        if m: self.ping_ttl = int(m.group(1))
        else: self.ping_ttl = ''
        
        m = re.search('Reply from ([0-9.]+):', self.ping_result)
        if m: self.ping_reply = (m.group(1))
        else: self.ping_reply = ''
        
        m = re.search('Minimum = ([0-9]+)ms', self.ping_result)
        if m: self.ping_delay = int(m.group(1))
        else: self.ping_delay = ''
       
        return 'Ping statistics for %s\n sent %s  recv %s  delay %s  ttl %s  reply from %s' % (ip, self.ping_sent, self.ping_recv, self.ping_delay, self.ping_ttl, self.ping_reply)
       
       
    def dns_rlook(self, ip=''):
        """
        Reverse DNS lookup
        """
        return socket.gethostbyaddr(ip)[0]
           
   
    def dns_look(self, name=''):
        """
        Normal DNS lookup
        """
        return socket.gethostbyname(name)
        
        
    def dns_look_suffix(self, name, suffix_list):
        """
        DNS lookup with auto appended suffix
        will try each entry in the suffix_list
        until a match is found
        """
        
        for suffix in suffix_list:
            res = name.lower() + '.' + suffix
            try: return socket.gethostbyname(res), res
            except: pass
            
      
    def trace(self, ip, name, max_ttl=30):
        """
        Traceroute
        """
        
        ttl = 1
        self.trace_list = []
        if self.verbose > 0: print 'tracing route to %s  -  %s' % (ip, name)
        
        while ttl <= max_ttl:
            self.test_ping(ip, ttl)
            hop_ip = self.ping_reply
           
            #reverse lookup and second ping to measure delay
            if hop_ip != '-':
                host_name = self.dns_rlook(hop_ip)
                self.test_ping(hop_ip)
           
            res = (ttl, self.ping_sent, self.ping_recv, self.ping_delay, self.ping_ttl, hop_ip, host_name)
            self.trace_list.append(res)
            if self.verbose > 0:
                print 'hop %s%s  ttl %s%s  delay %s%s ms  %s [%s]' % (res[0], self.space(res[0], 2), res[4], self.space(res[4], 3), self.space(res[3], 9), res[3], res[6], res[5])
            
            if ip in hop_ip: return self.trace_list
            ttl += 1
           
           
    def ping(self, ip='', count=1, ttl=255, timeout=300, size=32):
        """
        Ping
        """
        if not ip: ip = self.ip
        
        sent = recv = exp = 0
        self.ping_delay_list = []
        while sent < count:
            self.test_ping(ip, ttl, 1, timeout, size)
            if self.ping_delay != 'timed out':
                if ip not in self.ping_reply: exp += 1    #TTL Expired or Unreachable
                else: self.ping_delay_list.append(self.ping_delay)
               
            sent += 1
            recv += self.ping_recv
       
        try:
            avg_delay = sum(self.ping_delay_list) / (count - exp)
            max_delay = max(self.ping_delay_list)
            min_delay = min(self.ping_delay_list)
        except: avg_delay = max_delay = min_delay = 0
       
        self.ping_res = (ip, sent, recv, avg_delay, min_delay, max_delay)
       
        if self.verbose > 0:
            print '\n %s  sent %s  recv %s  Expired %s  avg %s ms  min %s ms  max %s ms' % (ip, sent, recv, exp, avg_delay, min_delay, max_delay)
       
        return self.ping_res   
       
       
    def scan(self, ip='', port_list=''):
        """Port Scanner"""
        if not ip: ip = self.ip
        if not port_list: port_list = self.port_list
        if 'int' in str(type(port_list)): port_list = [port_list]
        self.scan_dict = {}
       
        for port in port_list:
            res = self.test_port(port, ip)
            if 'fail' in res: self.scan_res = (ip, port, res[0], res[1], res[2])
            else: self.scan_res = (ip, port, 'ok', res)
            
            if self.verbose > 0: 
                if 'ok' in self.scan_res[2]: print self.scan_res[1], self.scan_res[2]
            self.scan_dict[port] = self.scan_res
            
        return self.scan_dict
        
        
    def get_http_proxy(self, url):
        """
        web capture via proxy
        """
        try:
            proxy = urllib2.ProxyHandler({'http': self.web_proxy})
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)
            res = urllib2.urlopen(url)
            return res.code, res.msg, res.url, res.read()
        
        except urllib2.HTTPError, e: return e.code, e.msg, e.url, e.read()
        except urllib2.URLError, e: return 0, 'url error', url, e.reason
        
        
    def get_http(self, url):
        """
        direct web capture
        """
        try: 
            res = urllib2.urlopen(url)
            return res.code, res.msg, res.url, res.read()
        
        except urllib2.HTTPError, e: return e.code, e.msg, e.url, e.read()
        except urllib2.URLError, e: return 0, 'url error', url, e.reason
        
        
    def get_http_auth(self, url, username, password):
        """
        direct web capture with username authentication
        """
        try:
            request = urllib2.Request(url)
            base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)
            return urllib2.urlopen(request)
        except urllib2.HTTPError, e: return e.code, e.msg, e.url, e.read()
        except urllib2.URLError, e: return 0, 'url error', url, e.reason
        
        
           
   
