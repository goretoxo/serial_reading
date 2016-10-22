#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Pedro Silva
# https://github.com/goretoxo/serial_reading.git
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##################
# backend utility to read output from DHT arduino examples and send it to 
# a graphite server

from time import time
from serial import Serial
from sys import exit
import logging
import socket
import argparse

CARBON_SERVER = '127.0.0.1'
CARBON_PORT = 2003
SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BAUDS = 9600
VERSION = '0.2'

def do_send(new_reading, text):
    """ connect to carbon server and send data """
    t = new_reading.split('.')[0]
    message = "sensor.values.{} {} {}".format( text, t, int(time()))
    logging.debug(message)
    sock = socket.socket()
    sock.connect((CARBON_SERVER, CARBON_PORT))
    sock.sendall(message)
    sock.close()

def context():
    """ read args, and start logging facilities"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug',
        help='show debug messages',
        action='store_true')
    parser.add_argument('-v', '--version',
        help='show version info',
        action='version',
        version=VERSION)
    parser.add_argument('-s','--serial',
        action='store',
        help = 'serial port')
    parser.add_argument('-p','--port',
        action='store',
        help = 'carbon server port')
    parser.add_argument('-c','--carbon',
        action='store',
        help = 'carbon server')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',level=logging.ERROR)
 
    if args.serial:
        global SERIAL_PORT
        SERIAL_PORT = args.serial
    if args.port:
        global CARBON_PORT
        CARBON_PORT = args.port
    if args.carbon:
        global CARBON_SERVER
        CARBON_SERVER = args.carbon

    logging.info('Carbon port: {}'.format(CARBON_PORT))
    logging.info('Carbon server: {}'.format(CARBON_SERVER))
    logging.info('Serial port: {}'.format(CARBON_SERVER))

def read_loop():
    """start serial and read from it, in loop """
    try:
      ser = Serial(SERIAL_PORT, SERIAL_BAUDS)
    except:
      logging.error("No device on {} ".format( SERIAL_PORT ))
      exit(1)
    flag = 0
    while 1:
      serial_line = ser.readline()
      logging.debug(serial_line)
  
      if(flag==1):
          message = 'temp '
          do_send(serial_line, message)
      if(flag==2):
          message = 'hum'
          do_send(serial_line, message)
          flag = 0

      if "Temperat" in serial_line:
          flag = 1
      if "Humid" in serial_line:
          flag = 2
      logging.debug(flag)
    ser.close() 

def main():
    context()
    read_loop()


if __name__ == "__main__":
    main()
