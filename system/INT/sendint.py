# -*- coding:utf-8 -*-

import sys
import json
from bitstring import BitArray
import time
import threading
import socket
from datetime import datetime

class PacketSender(object):
    """
    INT Packet Sender
    """

    def __init__(self, route_info):
        """
        Initialize with route information

        :param route_info: JSON string containing route information
        """
        print("good")
        self.route_info = json.loads(route_info)
        self.address_to_port = {
            '10.0.1.1': 5,
            '10.0.2.2': 4,
            '10.0.3.3': 4,
            '10.0.4.4': 3,
            '10.0.5.5': 4,
            '10.0.6.6': 4,
            '10.0.7.7': 5,
            '10.0.8.8': 4,
            '10.0.9.9': 3,
            '10.0.10.10': 5,
            '10.0.11.11': 3,
            '10.0.12.12': 6,
            '10.0.13.13': 6
        }
        self.port_map = {
            0: 2,
            1: 3,
            2: 4,
            3: 2,
            4: 3,
            5: 2,
            6: 3,
            7: 2,
            8: 2,
            9: 3,
            10: 2,
            11: 3,
            12: 2,
            13: 3,
            14: 4,
            15: 2,
            16: 3,
            17: 2,
            18: 2,
            19: 3,
            20: 4,
            21: 2,
            22: 2,
            23: 3,
            24: 4,
            25: 5,
            26: 2,
            27: 3,
            28: 4,
            29: 5
        }
        self.sleep_interval = 1

    def send_packets(self):
        """
        Send packets based on the route information
        """
        info = self.route_info

        addressList = info.get('addressList')
        print("ips:", addressList)
        portsLists = info.get('portsLists')
        print("ports:", portsLists)
        actId = 1
        sendTimes = 1
        listLen = len(portsLists)
        ports = []
        bitmap_list = [
            0b00000001, 0b00000001,  # bitmap
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
            0b00000001, 0b00000001,
        ]
        for i in range(listLen):
            portsList = portsLists[i]
            print("ipsnow:", portsList)
            address = addressList[i]
            byteRoute = ''
            converted_ports = [self.port_map[port] for port in portsList]
            # converted_ports[-1] = 5
            converted_ports[-1] = self.address_to_port[address]
            print("converted ports:", converted_ports)
            converted_ports.reverse()
            for port, bitmap in zip(converted_ports, bitmap_list):
                byteRoute = byteRoute + self.addRoute(port, bitmap)
            print("byteroute:", byteRoute)
            byteContent = self.byteDateToSend(byteRoute, actId)
            print("byteContent:", byteContent)
            # send packet async
            thread = threading.Thread(target=self.sendPacketByTime, args=(
                sendTimes, byteContent, address, actId))
            thread.setDaemon(False)
            thread.start()

    def addRoute(self, port, bitmap):
        """
        Convert a route switch port and bitmap to route byte info

        :param port: a switch port in route
        :param bitmap: a bitmap associated with the port
        :returns: a prettied binary port string concatenated with the bitmap
        """
        portOct = int(port) - 1
        portBin = bin(portOct)[2:]
        portBinPretty = '0' * (6 - len(portBin)) + portBin
        bitmapBin = bin(bitmap)[2:]
        bitmapPretty = '0' * (8 - len(bitmapBin)) + bitmapBin
        return portBinPretty + bitmapPretty

    def byteDateToSend(self, byteRoute, actId):
        """
        Convert traverse route byte info to a formatted byte info

        :param byteRoute: traverse route byte info
        :param actId: action id from controller
        :returns: a formatted byte info
        """
        byteRouteStr = '0' * (512 - int(len(byteRoute))) + byteRoute
        # byteStr = actIdBinStr + byteRouteStr
        byteContent = BitArray('0b' + byteRouteStr).bytes
        return byteContent

    def sendPacketByTime(self, sendTime, byteContent, address, actId):
        """
        Send INT packet in the given time

        :param sendTime: the time to send packet
        :param byteContent: the content to be send
        :param address: the target host IP address
        :param actId: the action ID receive from controller
        """
        startTime = time.time()
        i = 0
        times = 0

        # Start a thread to update the sleep interval from time.txt
        thread = threading.Thread(target=self.update_sleep_interval)
        thread.setDaemon(True)
        thread.start()

        while time.time() - startTime < sendTime:
            self.sendUDP(byteContent, address)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            dt_object = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S.%f')
            epoch_time = dt_object.timestamp()
            print(f"send to {address} at {epoch_time}")
            i = i + 1

            time.sleep(self.sleep_interval)
            times = times + 1
        endTime = time.time()
        p_rate = i / (endTime - startTime)
        print(f"Sent {i} packets to {address} at a rate of {p_rate:.2f} packets/second")

    def update_sleep_interval(self):
        """
        Update sleep interval by reading time.txt every 0.1 second
        """
        while True:
            try:
                with open('time.txt', 'r') as f:
                    self.sleep_interval = float(f.read().strip())
            except Exception as e:
                print(f"Error reading time.txt: {e}")
            time.sleep(0.1)

    def sendUDP(self, content, address):
        """
        Send traverse path via UDP

        :param content: traverse route content
        :param address: traverse target address
        """
        udpLink = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = (address, 2222)
        udpLink.sendto(content, addr)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: Missing route information")
        sys.exit(1)

    route_info = sys.argv[1]
    ps = PacketSender(route_info)
    ps.send_packets()
