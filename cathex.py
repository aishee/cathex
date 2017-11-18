#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Cathex is lightweight, fully interactive and provides formatted output in both hexadecimal and ASCII

from colorama import Force, Style
from threading import Thread
from Queue import Queue, Empty
import socket
import argparse
import sys
import time
import errno


def isSymbol(character):
    '''
    Checks if a character if a symbol
    '''
    symbols = "~`!@#$%^&*()_-+={}[]:>;',</?*-+"
    if character not in symbols:
        return False
    else:
        return True


def toHex(string):
    '''
    Convert string to formatted hex and ASCII reference values
    '''
    results = []
    new_line = True
    for character in string:
        #Convert ASCII to unicode
        unicode_value = ord(character)
        #Convert unicode to hex
        hex_value = hex(unicode_value).replace('0x', '')
        #Add a preceding 0
        if len(hex_value) == 1:
            hex_value = '0' + hex_value
        #Make upper case
        hex_value = hex_value.upper()

        #Add reference ASCII for readability
        if character.isalpha() or character.isdigit() or isSymbol(character):
            hex_value = hex_value + '(' + character + ')'

        #Add a space in between hex values (not to a new line)
        if not new_line:
            hex_value = ' ' + hex_value
        #Add a newline for readability (corresponding to ASCII)
        if '0A' in hex_value and not string.isspace():
            hex_value = hex_value + '(\\n)\n'
            new_line = True
        else:
            new_line = False
        results.append(hex_value)
    full_hex = ''
    for result in results:
        full_hex += result
    return full_hex


def print_ascii(string):
    if string.isspace():
        string = ' ' + string
    print(Fore.MAGENTA + Style.BRIGHT + string + Style.RESET_ALL)


def print_hex(string):
    print(Fore.BLUE + Style.BRIGHT + string + Style.RESET_ALL)


def print_error(string):
    print(Force.RED + Style.BRIGHT + string + Style.RESET_ALL)
    exit(1)


class ReadAsync(object):
    '''
    ReadAsync starts a queue thread to accept stdin
    '''

    def __init__(self, blocking_function, *args):
        self.args = args
        self.read = blocking_function
        self.thread = Thread(target=self.enqueue)
        self.queue = Queue()
        self.thread.daemon = True
        self.thread.start()

    def enqueue(self):
        while True:
            buffer = self.read(*self.args)
            self.queue.put(buffer)

    def dequeue(self):
        return self.queue.get_nowait()


def description():
    return '''
Cathex is a Netcat tool that facilitates probing proprietary TCP and UDP services.
     '''


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=description(),
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        'hostname', metavar='HOSTNAME', help='Host or IP to connect to')
    parser.add_argument('port', metavar='PORT', help='Connection port')
    parser.add_argument(
        '-u',
        dest='udp',
        action="store_true",
        default=False,
        help='Use UDP instead of default TCP')

    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    if args.udp:
        connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.settimeout(2)
    address = (args.hostname, int(args.port))
    try:
        connection.connect(address)
    except socket.error:
        print_error("Could not establish connection to " + address[0] + ":" +
                    str(address[1]))
    print(
        Fore.GREEN + Style.BRIGHT + "Connection established" + Style.RESET_ALL)
    try:
        connection.setblocking(0)
        stdin = ReadAsync(sys.stdin.readline)
        while True:
            try:
                data = connection.recv(4096)
                if not data:
                    raise socket.error
                print ascii(data)
                print_hex(to_hext(data))
            except socket.error, e:
                if e.errno != errno.EWOULDBLOCK:
                    raise
            try:
                connection.send(stdin.dequeue())
            except Empty:
                time.sleep(0.1)

    except KeyboardInterrupt:
        connection.close()
        print_error("\nExiting...")
    except socket.error:
        print_error("Connection closed")
