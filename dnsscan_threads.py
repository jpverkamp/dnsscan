#!/usr/bin/env python
import os
import sys
import dns.resolver
import Queue
import time
import threading

# Various settings
numthreads = 150
resultList = []
wq = Queue.Queue()

# Prefix to yield
def prefix_to_ips(prefix):
    if '/' in prefix:
        ip, size = prefix.split('/')
    else:
        ip = prefix
        size = 32
    ip = map(int, ip.split('.'))
    size = 2 ** (32 - int(size))
    for i in xrange(size):
        yield '.'.join(map(str, ip))
        ip[3] += 1
        for i in xrange(3, 0, -1):
            if ip[i] > 255:
                ip[i] = 0
                ip[i - 1] += 1

# Thread Launcher
def launchThreads(prefix,numthreads):
    global wq
    # Enqueing Stuff
    for ip in prefix_to_ips(prefix):
        wq.put(ip)
    # Spawning Threads
    for i in range(numthreads):
        t = threading.Thread(target=tRun)
        t.start()        
    while threading.active_count() > 1:
        time.sleep(0.1)

# Thread            
def tRun():
    global wq
    global resultList
    while not wq.empty():
        ip = wq.get()
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [ip]
        resolver.lifetime = 0.15
        target = 'google.com'
        try:
          answers = resolver.query(target, 'A')
          resultList.append('%s' % (ip))
        # If no response do nothing
        except (dns.resolver.NoAnswer, dns.resolver.NoNameservers), ex:
          pass
        # If timeout do nothing
        except dns.resolver.Timeout, ex:
          pass
        # If something else went sideways do nothing
        except:
          pass            

if __name__ == '__main__':
    # Process command line options
    import argparse
    parser = argparse.ArgumentParser(description = 'Scan prefixes for open resolvers')
    parser.add_argument('prefixes', nargs = argparse.REMAINDER, help = 'prefixes to scan')
    args = parser.parse_args()

    # Run scans, die properly on CTRL-C
    try: 
      for prefix in args.prefixes:
         launchThreads(prefix,numthreads)
    
      # Print results      
      for x in resultList:
         print x
      print "Number of open resolvers: %s" %(len(resultList))
      
    except KeyboardInterrupt, ex:
        pass
