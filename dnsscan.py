#!/usr/bin/env python

import os
import sys

try:
    import dns.resolver
except:
    print 'dnspython is required'
    print 'http://www.dnspython.org/'
    sys.exit(0)

def prefix_to_ips(prefix):
    '''Given a valid IPv4 prefix, generate all IP addresses.'''

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

def scan_prefix(prefix):
    '''Given an IPv4 prefix, launch a DNS query to each IP address.'''

    args = globals()['args']

    resolver = dns.resolver.Resolver()
    resolver.timeout = args.timeout

    target = args.hostname or 'google.com'

    for ip in prefix_to_ips(prefix):
        resolver.nameservers = [ip]

        # If we get an answer, it's open
        try:
            answers = resolver.query(target, 'A')
            print '%s,open' % (ip)

        # NoAnswer: Contacted a server but didn't get a valid response
        # NoNameservers: Couldn't get a valid answer from any of the nameservers
        # These probably mean it's closed
        except (dns.resolver.NoAnswer, dns.resolver.NoNameservers), ex:
            print '%s,closed' % (ip)
        
        # No response
        except dns.resolver.Timeout, ex:
            pass

if __name__ == '__main__':
    # Process command line options
    import argparse
    parser = argparse.ArgumentParser(description = 'Scan IPv4 prefixes for DNS resolvers')
    parser.add_argument('-t', '--timeout', type = float, default = 1.0, help = 'timeout for each request')
    parser.add_argument('-u', '--url', default = 'google.com', help = 'hostname to use as target')
    parser.add_argument('prefixes', nargs = argparse.REMAINDER, help = 'prefixes to scan')
    args = parser.parse_args()

    # Run scans, die nicely on Ctrl-C
    try:
        for prefix in args.prefixes:
            scan_prefix(prefix)
    except KeyboardInterrupt, ex:
        pass
    
