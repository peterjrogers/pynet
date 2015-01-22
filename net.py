import socket, re, time, urllib2, base64
from subprocess import Popen, PIPE
from tools import Tools

class Net(Tools):
    def __init__(self, ip='192.168.1.10', name='test', port=23, verbose=1):
        Tools.__init__(self)
        """
        Network tool kit
        1) Methods from the socket library are presented with descriptions from the man page https://docs.python.org/2/library/socket.html
        2) ping function using the windows cmd line parse method
        
        (c) 2012 - 2015 Intelligent Planet Ltd
        """
        
        self.init_net(ip, name, port)
               
        self.sleep = 0.1
        self.verbose = verbose
       
        self.recv_buffer = 1024
        self.error = 'fail'
        
        self.web_proxy = '172.19.193.122'
       
        self.port_list = [20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 161, 162, 179, 443, 520, 1719, 1720, 1985, 1998, 2000, 2427, 3389, 5060, 5900, 8080]
        #FTP(20, 21), SSH(22), Telnet(23), SMTP(25), DNS(53), DHCP(67, 68), TFTP(69), HTTP(80), SNMP(161, 162), BGP(179), HTTPS(443), RIP(520)
        #H.323(1719. 1720), HSRP(1985), XOT(1998), SCCP(2000), MGCP(2427), RDP(3389), SIP(5060), VNC(5900)
       
        self.http_get = 'GET /index.html HTTP/1.1 \r\n'
        self.http_host = 'Host: %s \r\n\r\n'
        
        
    def init_net(self, ip, name, port):
        """
        help: re-initialize the input values for the class
        usage: init_net(ip, name, port)
        example: init_net(ip='192.168.1.1', name='test', port=23)
        """
        self.ip = ip
        self.host_name = name
        self.port = port
       
       
    def socket_open(self, port, ip, timeout=0.2):
        """
        help: open a socket with the set timeout and reference as self.sock
        usage: socket_open(port, ip, timeout)
        example: socket_open(port=23, ip='192.168.1.1', timeout=0.5)
        output is null for normal operation
        """
        try:
            self.sock = socket.socket()
            self.socket_set_timeout(timeout)
            self.socket_connect(ip, port)
        except socket.error, e: return (self.error, 'socket_open', e)
        
        
    def socket_set_timeout(self, timeout):
        """
        help: set the socket timeout in seconds (float)
        Set a timeout on blocking socket operations. The value argument can be a nonnegative float expressing seconds, or None. If a float is given, subsequent socket operations will raise a timeout exception if the timeout period value has elapsed before the operation has completed. Setting a timeout of None disables timeouts on socket operations. s.settimeout(0.0) is equivalent to s.setblocking(0); s.settimeout(None) is equivalent to s.setblocking(1)
        usage: socket_set_timeout(timeout)
        example: socket_set_timeout(0.5)
        """
        try: self.sock.settimeout(timeout)
        except socket.error, e: return (self.error, 'socket_set_timeout', e)
        
        
    def socket_get_timeout(self):
        """
        help: Return the timeout in seconds (float) associated with socket operations, or None if no timeout is set.
        usage: socket_get_timeout()
        """
        try: return socket.gettimeout()
        except socket.error, e: return (self.error, 'socket_get_timeout', e)
        
        
    def socket_connect(self, ip, port):
        """
        help: Connect to a remote socket at address in the form (ip, port) Note: ip, port format is Tuple.
        usage: socket_connect(ip, port)
        example: socket_connect(ip='192.168.1.1', port=23)
        """
        try: self.sock.connect((ip, port))
        except socket.error, e: return (self.error, 'socket_connect', e)
       
       
    def socket_close(self):
        """
        Help: Close the socket. All future operations on the socket object will fail. The remote end will receive no more data (after queued data is flushed). Sockets are automatically closed when they are garbage-collected.
        usage: socket_close()
        """
        try: self.sock.close()
        except: pass
       
       
    def socket_get_peer_name(self):
        """
        help: Return the remote address to which the socket is connected. This is useful to find out the port number of a remote IPv4/v6 socket, for instance.
        usage: socket_get_peer_name()
        """
        try: return self.sock.getpeername()
        except socket.error, e: return (self.error, 'socket_get_peer_name', e)
        
        
    def socket_get_sock_name(self):
        """
        help: return the socket's own address. This is useful to find out the port number of an IPv4 / v6 socket.
        usage: socket_get_sock_name()
        """
        try: return self.sock.getsockname()
        except socket.error, e: return (self.error, 'socket_get_sock_name', e)
        
        
    def socket_get_fqdn(self, name=''):
        """
        help: Return a fully qualified domain name for name. If name is omitted or empty, it is interpreted as the local host. To find the fully qualified name, the hostname returned by gethostbyaddr() is checked, followed by aliases for the host, if available. The first name which includes a period is selected. In case no fully qualified domain name is available, the hostname as returned by gethostname() is returned.
        usage: socket_get_fqdn(name='4.4.4.4')
        """
        try: return socket.getfqdn(name)
        except socket.error, e: return (self.error, 'socket_get_fqdn', e)
        
        
    def socket_get_host_by_name(self, hostname):
        """
        help: Translate a host name to IPv4 address format, extended interface. Return a triple (hostname
        aliaslist, ipaddrlist) where hostname is the primary host name responding to the given ip_address,
        aliaslist is a (possibly empty) list of alternative host names for the same address, and ipaddrlist is a
        list of IPv4 addresses for the same interface on the same host (often but not always a single address). .
        usage: socket_get_host_by_name(name='www.google.com')
        output is (hostname, aliaslist, ipaddrlist)
        """
        try: return socket.gethostbyname_ex(hostname)
        except socket.error, e: return (self.error, 'socket_get_host_by_name', e)
        
        
    def socket_recv(self):
        """
        help: Receive data from the socket. The return value is a string representing the data received. The maximum amount of data to be received at once is specified by self.recv_buffer
        usage: self.sock.recv(self.recv_buffer)
        """
        try: return self.sock.recv(self.recv_buffer)
        except socket.error, e: return (self.error, 'socket_recv', e)
       
       
    def socket_send(self, data):
        """
        help: Send data to the socket. The socket must be connected to a remote socket. The optional flags argument has the same meaning as for recv() above. Returns the number of bytes sent. Applications are responsible for checking that all data has been sent; if only some of the data was transmitted, the application needs to attempt delivery of the remaining data.
        usage: socket_send(data)
        output is the number of bytes sent
        """
        try: return self.sock.send(data)
        except socket.error, e: return (self.error, 'socket_send', e)
        
        
    def socket_shutdown(self, how):
        """
        help: Shut down one or both halves of the connection. If how is SHUT_RD, further receives are disallowed. If how is SHUT_WR, further sends are disallowed. If how is SHUT_RDWR, further sends and receives are disallowed. Depending on the platform, shutting down one half of the connection can also close the opposite half (e.g. on Mac OS X, shutdown(SHUT_WR) does not allow further reads on the other end of the connection).
        usage: socket_shutdown(how='SHUT_WR')
        output is On success, zero is returned. On error, -1 is returned
        """
        try: return self.sock.shutdown(how)
        except socket.error, e: return (self.error, 'socket_shutdown', e)
       
       
    def test_http(self, port, ip):
        """
        help: connect to a remote port and collect data by using http methods
        usage: test_http(port, ip)
        output is the data returned from the remote http server or details of the connection error
        """
        #open the connection
        error = self.socket_open(port, ip)
        if error: return error
        #make a get request to the server
        self.socket_send(self.http_get)
        self.socket_send(self.http_host % (self.ip))
        return self.socket_recv()
       
       
    def test_port(self, port, ip, send=''):
        """
        help: tcp port test, will open a session to the host / port and return any received data
        usage: test_port(port, ip, send)    #send is optional
        example: test_port(80, '4.4.4.4')
        """
        #open the connection
        error = self.socket_open(port, ip)
        if error: return error
        #send data and return the data read from the socket
        if send:
            self.socket_send(send)
            time.sleep(self.sleep)  
        return self.socket_recv()
        
        
    def test_port_front(self, port, ip, send=''):
        """
        help: front end function to implement custom behaviour for protocols - i.e. http
        usage: test_port_front(port=80, ip='192.168.1.1', send='')
        """
        if port == 80: print 'http test' ; return self.test_http(port, ip)
        return self.test_port(port, ip)
       
       
    def test_ping(self, ip, ttl=255, count=1, timeout=300, size=32, verbose=1):
        """
        help: ping test function that uses the windows command line ping tool and parses the output text
        usage: batch test_ping(ip='172.22.25.135', ttl=255, count=1, timeout=300, size=32, verbose=3)
        output is (ip, ping_sent, ping_recv, ping_delay, ping_ttl, ping_reply)
        """
        #run the command
        cmd = "p = Popen('ping -n %s -w %s -i %s -l %s %s', stdout=PIPE)" % (count, timeout, ttl, size, ip)
        exec(cmd)
        
        #get the result from stout
        rows = p.stdout.read().split('\n')
        if verbose > 1: print rows
        ttl = '' ; delay = '' ; reply = '' ; recv = ''
        #parse the text
        for row in rows:
            if verbose > 0: print row
            
            res = row.split()
            if verbose > 2: print res
            
            if 'Packets:' in row:    #Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),
                recv = res[6].strip(',')
            
            if 'Reply from' in row:    #Reply from 172.22.25.132: bytes=32 time=10ms TTL=247
                ttl = int(res[-1][4:])
                delay = int(res[4][5:].strip('ms'))
                reply = res[2].strip(':')
             
        print (ip, count, recv, delay, ttl, reply)
        return ip, count, recv, delay, ttl, reply
       
       
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
        
        
           
   
