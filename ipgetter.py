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
from sys import stdout, stderr
from sys import version_info
from functools import wraps
from os import path


DEFAULT_SERVER_LIST_LOCATION=path.join(path.abspath("."), "server-list")

PY3K = version_info >= (3, 0)

if PY3K:
    import urllib.request as urllib
else:
    import urllib2 as urllib

__version__ = "0.4"


def timeout(seconds, error_message='Function call timed out'):
    '''
    Decorator that provides timeout to a function
    '''
    def decorated(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        @wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return wrapper
    return decorated


@timeout(120)
def myip():
    return IPgetter().get_externalip()

def get_server_list(server_file = None):
    locations = [DEFAULT_SERVER_LIST_LOCATION]
    if server_file:
        locations.insert(0, server_file)

    for fname in locations:
        try:
            list_file = open(fname)
            break
        except FileNotFoundError:
            print("ERROR: '{}', file not found".format(fname), file = stderr)
        except:
            print("ERROR: Could not open file '{}'".format(fname))

    if not list_file:
        print("Could not open a server list file successfully", file = stderr)
        print("Exiting ...", file = stderr)
        exit(1)

    server_list = []

    line = list_file.readline()
    while line != "": # TODO maybe make this a seperate function that also does some regex checking
        line = line.strip()
        if len(line) != 0 and not line.startswith("#"):
            server_list.append(line)
        line = list_file.readline()
    list_file.close()
    
    return server_list


class IPgetter(object):

    '''
    This class is designed to fetch your external IP address from the internet.
    It is used mostly when behind a NAT.
    It picks your IP randomly from a serverlist to minimize request overhead
    on a single server
    '''

    def __init__(self, server_file = None):
        self.server_list = get_server_list(server_file)

    def get_externalip(self):
        '''
        This function gets your IP from a random server
        '''

        random.shuffle(self.server_list)
        myip = ''
        for server in self.server_list:
            myip = self.fetch(server)
            if myip != '':
                return myip
            else:
                continue
        return ''

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
            return myip if len(myip) > 0 else ''
        except Exception:
            return ''
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
