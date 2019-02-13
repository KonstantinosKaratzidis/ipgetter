from setuptools import setup

long_desc = """This module is designed to fetch your external IP address from the internet.
It is used mostly when behind a NAT. It picks your IP randomly from a serverlist
to minimize request overhead on a single server."""

setup(
    name='ipgetter',
    version=open("version").read().strip(),
    author='Fernando Giannasi <phoemur@gmail.com>',

    description="Utility to fetch your external IP address",
    license="Public Domain",
    classifiers=[
        'Environment :: Console',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
    ],

    packages = ["ipgetter"],

    long_description=long_desc
)
