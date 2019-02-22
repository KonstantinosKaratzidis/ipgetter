#!/usr/bin/env python
"""
This module is designed to fetch your external IP address from the internet.
It is used mostly when behind a NAT.
It picks your IP randomly from a serverlist to minimize request
overhead on a single server

If you want to add or remove your server from the list contact me on github


API Usage
=========

    >>> import ipgetter
    >>> myip = ipgetter.myip()
    >>> myip
    '8.8.8.8'

    >>> ipgetter.IPgetter().test()

    Number of servers: 47
    IP's :
    8.8.8.8 = 47 ocurrencies

"""
import re
import random
import signal
from sys import stderr, version_info
from functools import wraps

from .server_list import DEFAULT_SERVERS

PY3K = version_info >= (3, 0)
if PY3K:
    import urllib.request as urllib
else:
    import urllib2 as urllib

class ServerListNotFound(Exception):
    pass

def get_server_list(fname = None, raise_error = False):
    if not fname: 
        return DEFAULT_SERVERS

    try:
        server_list = []

        # TODO maybe make this a seperate function that also does some regex checking
        with open(fname) as list_file:
            line = list_file.readline()
            while line != "":
                line = line.strip()
                if len(line) != 0 and not line.startswith("#"):
                    server_list.append(line)
                line = list_file.readline()
        
    except:
        print("Could not open server file.", file = stderr)
        if raise_error:
            raise ServerListNotFound
        return DEFAULT_SERVERS
    
    return server_list

def timeout_handler(signum, frame):
    raise ConnectionTimeout

class ConnectionTimeout(Exception):
    pass

class MaxTimesExceeded(Exception):
    pass

class IPgetter(object):

    '''
    This class is designed to fetch your external IP address from the internet.
    It is used mostly when behind a NAT.
    It picks your IP randomly from a serverlist to minimize request overhead
    on a single server
    '''

    def __init__(self, server_file = None):
        self.server_list = get_server_list(server_file)

    def get_externalip(self, timeout = 30, max_tries = 5):
        '''
        This function gets your IP from a random server,
        timeouts marks the time in seconds after which the function will
        try to connect to another server, should the first one fail.
        Setting max_tries to None will test all servers until an ip is found.
        On failure MaxTimesExceeded is returned.
        '''

        def timeout_handler():
            raise ConnectionTimeout

        if max_tries is None:
            servers = random.shuffle(self.server_list)
        else:
            servers = random.sample(self.server_list, max_tries)

        signal.signal(signal.SIGALRM, timeout_handler)

        for server in servers:
            myip = None

            signal.alarm(timeout)
            try:
                myip = self.fetch(server)
            except ConnectionTimeout:
                pass
            finally:
                signal.alarm(0)

            if myip is not None:
                return myip
        
        # if we didnt return an ip, it means we needed more tries than max_tries
        raise MaxTimesExceeded

    def fetch(self, server):
        '''
        This function gets your IP from a specific server
        '''
        url = None
        opener = urllib.build_opener()
        opener.addheaders = [('User-agent',
                              "Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0")]

        try:
            url = opener.open(server)
            content = url.read()

            # Didn't want to import chardet. Prefered to stick to stdlib
            if PY3K:
                try:
                    content = content.decode('UTF-8')
                except UnicodeDecodeError:
                    content = content.decode('ISO-8859-1')

            m = re.search(
                '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',
                content)
            myip = m.group(0)
            return myip if len(myip) > 0 else None
        except Exception:
            return None
        finally:
            if url:
                url.close()

    def test(self):
        '''
        This functions tests the consistency of the servers
        on the list when retrieving your IP.
        All results should be the same.
        '''

        resultdict = {}
        for server in self.server_list:
            resultdict.update(**{server: self.fetch(server)})

        ips = sorted(resultdict.values())
        ips_set = set(ips)
        print('\nNumber of servers: {}'.format(len(self.server_list)))
        print("IP's :")
        for ip, ocorrencia in zip(ips_set, map(lambda x: ips.count(x), ips_set)):
            print('{0} = {1} ocurrenc{2}'.format(ip if len(ip) > 0 else 'broken server', ocorrencia, 'y' if ocorrencia == 1 else 'ies'))
        print('\n')
        print(resultdict)


if __name__ == '__main__':
    print(myip())
