#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import os


def gen_random_hex(length):
    '''
    Generate a hex string
    '''
    hex_string = os.urandom(length - 1)
    hex_string += '\x0a'
    return hex_string


host = '127.0.0.1'
port = 12345

s = socket.socket()
s.bind((host, port))
s.listen(5)

try:
    while True:
        c, addr = s.accept()
        print 'Connection established from', addr[0], ':', addr[1]
        c.send('Hello you')
        c.send('Test - enter string:')
        data = c.recv(1024)
        print 'Test - Received: ', data
        c.send('Test - Received: ' + data + '\n')

        c.send('Hex test - enter length: ')
        data = c.recv(1024)

        try:
            hex_length = int(data)
        except ValueError:
            c.send('You must enter a number. Default 10.\n')
            hex_length = 10
        hex_string = gen_random_hex(hex_length)
        c.send('Sending hex string...\n\n')
        print 'Hex test - sending: ', hex_string
        c.send(hex_string)

        c.close()
        print 'Closed connection to ', addr[0], ':', addr[1]
except KeyboardInterrupt:
    c.close()
    print '\nExiting...'
    exit(0)
