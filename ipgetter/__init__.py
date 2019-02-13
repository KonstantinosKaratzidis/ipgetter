from ipgetter.ip_getter import IPgetter

__version__ = "0.4"

if __name__ == "__main__":
    getter = IPgetter()
    print(getter.get_externalip())
