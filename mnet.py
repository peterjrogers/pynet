import Queue, threading, socket, time, sys, re, urllib2
from subprocess import Popen, PIPE

from tools import Tools
from net import Net

#queue method based on http://www.ibm.com/developerworks/aix/library/au-threadingpython/
#http://www.blog.pythonlibrary.org/2012/08/01/python-concurrency-an-example-of-a-queue/
       
       
class Mnet(Net, Tools):
    def __init__(self, verbose=1, maxq=200):
        Net.__init__(self)
        Tools.__init__(self)
        
        """
        Multithreaded network tools
        
        """
        
        self.verbose = verbose
        self.maxq = maxq
        
        self.timeout = 0.2    #
        self.buffers = 256    #for check_port
        
        #test lists
        #self.ip_list = open('c:/bip_ip.csv').read().split('\n')
        #self.host_list = open('c:/win7.csv').read().split('\n')
        
        
        
    def mt_base(self, label, cmd):
        self.pos = 0
        self.sleep = 0.005    #0.01 limits requests to 100 per second on dns servers
        self.out = {}
        self.label = label
        self.cmd = cmd
    
    
    def mt_dns_rlook(self, ip_list):    #reverse DNS lookup
        self.mt_base('Reverse DNS lookup', 'self.rlook(input)')
        return self.mt_go(ip_list)

        
    def mt_dns_look(self, name_list):    #normal DNS lookup
        self.mt_base('Normal DNS lookup', 'self.look(input)')
        return self.mt_go(name_list)
        
        
    def mt_port_spmip(self, ip_list, port):    #check single port on multiple IP's
        self.port = port
        self.buffers = 256
        self.mt_base('Single port multi IP', 'self.spmip(input)')
        self.sleep = 0.05
        return self.mt_go(ip_list)
        
        
    def mt_port_sipmp(self, port_list, ip):    #check multiple port on single IP
        self.ip = ip
        self.buffers = 256
        self.mt_base('Multi port single IP', 'self.sipmp(input)')
        self.sleep = 0.05
        return self.mt_go(port_list)
        
    
    def mt_ping(self, ip_list, count=1, timeout=300, ttl=30, size=32):    #ping test
        self.ping_count = count
        self.ping_timeout = timeout
        self.ttl = ttl
        self.ping_size = size
        self.mt_base('Ping test', 'self.ping(input)')
        return self.mt_go(ip_list)
        
       
    def mt_trace(self, ip, ttl=20, timeout=300, size=32):    #traceroute - send all ttl values in parrallel
        self.ping_count = 1
        self.ping_timeout = timeout
        self.ping_size = size
        self.ip = ip
        ttl += 1
        ttl_range = range(ttl)[1:]
        self.mt_base('Traceroute', 'self.trace(input)')
        self.mt_go(ttl_range)
        return self.trace_view()
        
        
    def mt_http(self, url_list, buffer=16384):    #download http
        self.buffer = buffer
        self.mt_base('Download http', 'self.http(input)')
        return self.mt_go(url_list)     
    
        
    def mt_go(self, in_list):    #build queue and launch threads
        if not in_list: return
        if 'str' in str(type(in_list)): in_list = [in_list]
        
        if len(in_list) > self.maxq: self.qlen = self.maxq
        else: self.qlen = len(in_list)
        
        queue = Queue.Queue()
        if self.verbose > 0: print '%s for %d items' % (self.label, len(in_list))
   
        for i in range(self.qlen):    #spawn a pool of threads, and pass them queue instance
            t = Go(queue, self)
            t.setDaemon(True)
            t.start()    #load the queue
    
        for item in in_list:    #populate queue with data
            input = in_list[self.pos]
            queue.put(input)
            sys.stdout.write('.')
            self.pos += 1
            time.sleep(self.sleep)
       
        queue.join()    #wait on the queue until everything has been processed
        queue = ''
        print '\n'
        return self.out
        
        
    def trace(self, ttl):
        """Traceroute"""

        self.ttl = ttl

        host_name = ''
        self.test_ping(self.ip)
        hop_ip = self.ping_reply
        res = (ttl, self.ping_sent, self.ping_recv, self.ping_delay, self.ping_ttl, hop_ip, host_name)
        
        if hop_ip == self.ip: return res
        
        if hop_ip == '-': return res
        
        #reverse lookup and second ping to measure delay
        if  self.verbose != -1:
            res = self.dns_rlook(hop_ip)
            if res: host_name = res
            
            self.ttl = 30
            self.test_ping(hop_ip)
            res = (ttl, self.ping_sent, self.ping_recv, self.ping_delay, self.ping_ttl, hop_ip, host_name)
            
            if self.verbose > 1:
                print 'hop %s  ttl %s  delay %s ms  %s [%s]' % (res[0], res[4], res[3], res[6], res[5])
               
            return res

    """    
    def test_ping(self, ip):    #self.ping_count, self.timeout, self.ttl, self.ip
        self.ping_sent = self.ping_recv = self.ping_delay = self.ping_reply = self.ping_ttl = 0
        cmd = "p = Popen('ping -n %s -w %s -i %s -l %s %s', stdout=PIPE)" % (self.ping_count, self.ping_timeout, self.ttl, self.ping_size, ip)
        exec(cmd)
        self.ping_reply = '-'
        self.ping_result = p.stdout.read()
       
        m = re.search('Sent = ([0-9]+),', self.ping_result)
        if m:
            self.ping_sent = int(m.group(1))
        m = re.search('Received = ([0-9]+),', self.ping_result)
        if m:
            self.ping_recv = int(m.group(1))
        m = re.search('TTL=([0-9]+)', self.ping_result)
        if m:
            self.ping_ttl = int(m.group(1))
        m = re.search('Reply from ([0-9.]+):', self.ping_result)
        if m:
            self.ping_reply = (m.group(1))
        m = re.search('Minimum = ([0-9]+)ms', self.ping_result)
        if m:
            self.ping_delay = int(m.group(1))
        else:
            self.ping_delay = 'timed out'
       
        if self.verbose > 3: print self.ping_result
        if self.verbose > 1: print '\nPing statistics for %s\n sent %s  recv %s  delay %s  ttl %s  reply from %s' % (ip, self.ping_sent, self.ping_recv, self.ping_delay, self.ping_ttl, self.ping_reply)
        return ip, self.ping_sent, self.ping_recv, self.ping_delay, self.ping_ttl, self.ping_reply
    """
        
        
    def test_ping(self, ip, ttl=255, count=1, timeout=300, size=32, verbose=1):
        """
        help: ping test function that uses the windows command line ping tool and parses the output text
        usage: batch test_ping(ip='172.22.25.132', ttl=255, count=1, timeout=300, size=32, verbose=3)
        output is (ip, sent, recv, delay, ttl, reply)
        """
        #run the command
        cmd = "p = Popen('ping -n %s -w %s -i %s -l %s %s', stdout=PIPE)" % (count, timeout, ttl, size, ip)
        exec(cmd)
        
        #get the result from stout
        rows = p.stdout.read().split('\n')
        ttl = '-' ; delay = '-' ; reply = '-' ; recv = '-'
        #parse the text
        for row in rows:            
            res = row.split()
            
            if 'Packets:' in row:    #Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),
                recv = res[6].strip(',')
            
            if 'Reply from' in row:    #Reply from 172.22.25.132: bytes=32 time=10ms TTL=247
                ttl = res[-1][4:]
                delay = res[4][5:].strip('ms')
                reply = res[2].strip(':')

        return ip, count, recv, delay, ttl, reply
        
    
    def check_port(self, ip, port):
        try:
            sock = socket.socket()
            sock.settimeout(self.timeout)
            sock.connect((ip, port))
            recv_data = sock.recv(self.buffers)
            return ip, port, recv_data
        
        except socket.error, e:
            return ip, port, 'fail', str(e)
        
        finally: sock.close()
        
    
    def trace_view(self):    #view trace results and return dict
        out = {}
        if self.verbose > -1: print 'tracing route to %s' % self.ip
        for key in self.out: 
            hop = key
            s_hop = self.space(hop)
            res = self.out[key]
            try: delay = res[2]
            except: delay = 'fail'
            s_delay = self.space(delay, 10)
            try: reply = res[4]
            except: reply = 'fail'
            s_reply = self.space(reply, 16)
            try: name = res[5]
            except: name = 'fail'
            if self.verbose > -1: print 'hop %s%s delay %s ms%s %s%s %s' % (hop, s_hop, delay, s_delay, reply, s_reply, name)
            out[hop] = [res]
            if str(self.ip.lstrip().rstrip()) == str(reply.lstrip().rstrip()): return out
        return out
        
        
class Go(threading.Thread):
    
    def __init__(self, queue, mt):    #mt = inherited values from Mnet
        threading.Thread.__init__(self)
        self.queue = queue
        self.mt = mt
        self.verbose = mt.verbose
        
        """
        Multi Thread Functions
        """   
        
     
    def run(self):
        while 1:
            input = self.queue.get()    #get input from the queue
            exec(self.mt.cmd)    #goto the function
           
           
    def http(self, url):
        """Retreive data via http"""
        
        res = 'fail', url
        try: 
            res = urllib2.urlopen(url).read(self.mt.buffer) 
        except: pass
        finally:
            if self.verbose > 2: print res
            self.mt.out[url] = res
            self.queue.task_done()
                  
               
    def rlook(self, ip):
        """Reverse DNS lookup"""
        
        res = 'fail', '', ip
        try: res = socket.gethostbyaddr(ip)
        except: pass
        finally:
            if self.verbose > 2: print res
            self.mt.out[ip] = res[0]
            self.queue.task_done()
       
       
    def look(self, name):
        """Normal DNS lookup"""
        
        res = 'fail', name
        try: res = socket.gethostbyname(name), name
        except: pass
        finally:
            if self.verbose > 2: print res
            self.mt.out[name] = res[0]
            self.queue.task_done()
            
       
    def spmip(self, ip):
        """Check single port on multiple IP's"""
        
        id = ip + ':' + str(self.mt.port)
        res = id, 'fail'
        try: res = self.mt.check_port(ip, self.mt.port)
        except: pass
        finally:
            if self.verbose > 2: print res
            self.mt.out[id] = res[2:]
            self.queue.task_done()
            
            
    def sipmp(self, port):
        """Check multiple port on single IP"""
        
        id = self.mt.ip + ':' + str(port)
        res = id, 'fail'
        try: res = self.mt.check_port(self.mt.ip, port)
        except: pass
        finally:
            if self.verbose > 2: print res
            self.mt.out[id] = res[2:]
            self.queue.task_done()
        
            
    def ping(self, ip):
        """Ping test"""
        
        res = ip, 'fail'
        try: res = self.mt.test_ping(ip)
        except: pass
        finally:
            if self.verbose > 2: print res
            self.mt.out[res[0]] = res[1:]
            self.queue.task_done()
            
       
    def trace(self, ttl):
        """Traceroute"""
        
        res = ttl, 'fail', self.mt.ip
        try: res = self.mt.trace(ttl)
        except: pass
        finally:
            if self.verbose > 1: print res
            self.mt.out[res[0]] = res[1:]
            self.queue.task_done()

    
    
