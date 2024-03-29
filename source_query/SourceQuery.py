# Work: getInfo(), getPlayers(), getChallenge(), getRules(), getPing()
# Support: Source Servers, GoldSrc servers, The Ship Servers
# ToDo: Bugfixes

import socket
import struct
import sys
import time

from tg.utils import markdown_v2_escape, markdown_v2_bold

__author__ = 'Dasister'
__site__ = 'http://21games.ru'
__description__ = 'Simple Query Class for VALVe servers'

A2S_INFO = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00'
A2S_PLAYERS = b'\xFF\xFF\xFF\xFF\x55'
A2S_RULES = b'\xFF\xFF\xFF\xFF\x56'

S2A_INFO_SOURCE = chr(0x49)
S2A_INFO_GOLDSRC = chr(0x6D)


class SourceQuery(object):
    is_third = False
    __sock = None
    __challenge = None

    def __init__(self, addr, port=27015, timeout=5.0):
        self.host = addr + ':' + str(port)
        self.ip, self.port, self.timeout = socket.gethostbyname(addr), port, timeout
        if sys.version_info >= (3, 0):
            self.is_third = True

    def disconnect(self):
        """ Close socket """
        if self.__sock is not None:
            self.__sock.close()
            self.__sock = False

    def connect(self):
        """ Opens a new socket """
        self.disconnect()
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.settimeout(self.timeout)
        self.__sock.connect((self.ip, self.port))

    def get_ping(self):
        """ Get ping to server """
        return self.get_info()['Ping']

    def get_server(self, markdown_v2=False):
        s = 'Информация о сервере:\n\n'

        players = self.get_players()
        res = self.get_info()
        s += 'Название: ' + (res['Hostname'] if not markdown_v2 else markdown_v2_bold(res['Hostname'])) + '\n'
        s += 'Адрес сервера: ' + (self.host if not markdown_v2 else markdown_v2_escape(self.host)) + '\n'
        s += 'Карта: ' + (res['Map'] if not markdown_v2 else markdown_v2_bold(res['Map'])) + '\n'
        s += 'Онлайн: ' + "%i/%i" % (res['Players'], res['MaxPlayers']) + '\n'

        s += '\n'

        s += 'Игроки онлайн:\n'
        if len(players) > 0:
            for player in players:
                if markdown_v2:
                    player['Name'] = markdown_v2_bold(player['Name'])
                    player['Frags'] = markdown_v2_escape(str(player['Frags']))
                s += str(player['id']) + (
                    "." if not markdown_v2 else "\\.") + " {Name}, фраги: {Frags}, время: {PrettyTime}".format(
                    **player) + '\n'
        else:
            s += 'Сервер пуст ' + u'\U0001F622'

        return s

    def get_info(self):
        """ Retrieves information about the server including, but not limited to: its name, the map currently being played, and the number of players. """
        if self.__sock is None:
            self.connect()
        self.__sock.send(A2S_INFO)
        before = time.time()
        try:
            data = self.__sock.recv(4096)
        except:
            return False

        after = time.time()
        data = data[4:]

        result = {}

        header, data = self.__get_byte(data)
        result['Ping'] = int((after - before) * 1000)
        if chr(header) == S2A_INFO_SOURCE:
            result['Protocol'], data = self.__get_byte(data)
            result['Hostname'], data = self.__get_string(data)
            result['Map'], data = self.__get_string(data)
            result['GameDir'], data = self.__get_string(data)
            result['GameDesc'], data = self.__get_string(data)
            result['AppID'], data = self.__get_short(data)
            result['Players'], data = self.__get_byte(data)
            result['MaxPlayers'], data = self.__get_byte(data)
            result['Bots'], data = self.__get_byte(data)
            dedicated, data = self.__get_byte(data)
            if chr(dedicated) == 'd':
                result['Dedicated'] = 'Dedicated'
            elif dedicated == 'l':
                result['Dedicated'] = 'Listen'
            else:
                result['Dedicated'] = 'SourceTV'

            os, data = self.__get_byte(data)
            if chr(os) == 'w':
                result['OS'] = 'Windows'
            elif chr(os) in ('m', 'o'):
                result['OS'] = 'Mac'
            else:
                result['OS'] = 'Linux'
            result['Password'], data = self.__get_byte(data)
            result['Secure'], data = self.__get_byte(data)
            if result['AppID'] == 2400:  # The Ship server
                result['GameMode'], data = self.__get_byte(data)
                result['WitnessCount'], data = self.__get_byte(data)
                result['WitnessTime'], data = self.__get_byte(data)
            result['Version'], data = self.__get_string(data)
            edf, data = self.__get_byte(data)
            try:
                if edf & 0x80:
                    result['GamePort'], data = self.__get_short(data)
                if edf & 0x10:
                    result['SteamID'], data = self.__get_long_long(data)
                if edf & 0x40:
                    result['SpecPort'], data = self.__get_short(data)
                    result['SpecName'], data = self.__get_string(data)
                if edf & 0x10:
                    result['Tags'], data = self.__get_string(data)
            except:
                pass
        elif chr(header) == S2A_INFO_GOLDSRC:
            result['GameIP'], data = self.__get_string(data)
            result['Hostname'], data = self.__get_string(data)
            result['Map'], data = self.__get_string(data)
            result['GameDir'], data = self.__get_string(data)
            result['GameDesc'], data = self.__get_string(data)
            result['Players'], data = self.__get_byte(data)
            result['MaxPlayers'], data = self.__get_byte(data)
            result['Version'], data = self.__get_byte(data)
            dedicated, data = self.__get_byte(data)
            if chr(dedicated) == 'd':
                result['Dedicated'] = 'Dedicated'
            elif dedicated == 'l':
                result['Dedicated'] = 'Listen'
            else:
                result['Dedicated'] = 'HLTV'
            os, data = self.__get_byte(data)
            if chr(os) == 'w':
                result['OS'] = 'Windows'
            else:
                result['OS'] = 'Linux'
            result['Password'], data = self.__get_byte(data)
            result['IsMod'], data = self.__get_byte(data)
            if result['IsMod']:
                result['URLInfo'], data = self.__get_string(data)
                result['URLDownload'], data = self.__get_string(data)
                data = self.__get_byte(data)[1]  # NULL-Byte
                result['ModVersion'], data = self.__get_long(data)
                result['ModSize'], data = self.__get_long(data)
                result['ServerOnly'], data = self.__get_byte(data)
                result['ClientDLL'], data = self.__get_byte(data)
            result['Secure'], data = self.__get_byte(data)
            result['Bots'], data = self.__get_byte(data)

        return result

    # <------------------getInfo() End -------------------------->

    def get_challenge(self):
        """ Get challenge number for A2S_PLAYER and A2S_RULES queries. """
        if self.__sock is None:
            self.connect()
        self.__sock.send(A2S_PLAYERS + b'0xFFFFFFFF')
        try:
            data = self.__sock.recv(4096)
        except:
            return False

        self.__challenge = data[5:]

        return True

    # <-------------------getChallenge() End --------------------->

    def get_players(self, escape=False):
        """ Retrieve information about the players currently on the server. """
        if self.__sock is None:
            self.connect()
        if self.__challenge is None:
            self.get_challenge()

        self.__sock.send(A2S_PLAYERS + self.__challenge)
        try:
            data = self.__sock.recv(4096)
        except:
            return False

        data = data[4:]

        header, data = self.__get_byte(data)
        num, data = self.__get_byte(data)
        result = []
        try:
            for i in range(num):
                player = {}
                data = self.__get_byte(data)[1]
                player['id'] = i + 1  # ID of All players is 0
                player['Name'], data = self.__get_string(data)
                player['Frags'], data = self.__get_long(data)
                player['Time'], data = self.__get_float(data)
                ftime = time.gmtime(int(player['Time']))
                player['FTime'] = ftime
                if ftime.tm_hour > 0:
                    player['PrettyTime'] = time.strftime('%H:%M:%S', ftime)
                else:
                    player['PrettyTime'] = time.strftime('%M:%S', ftime)
                result.append(player)
        except Exception:
            pass

        return result

    # <-------------------getPlayers() End ----------------------->

    def get_rules(self):
        """ Returns the server rules, or configuration variables in name/value pairs. """
        if self.__sock is None:
            self.connect()
        if self.__challenge is None:
            self.get_challenge()

        self.__sock.send(A2S_RULES + self.__challenge)
        try:
            data = self.__sock.recv(4096)
            if data[0] == 254:
                num_packets = data[8] & 15
                packets = [' ' for i in range(num_packets)]
                for i in range(num_packets):
                    if i != 0:
                        data = self.__sock.recv(4096)
                    index = data[8] >> 4
                    packets[index] = data[9:]
                data = bytes()
                for i, packet in enumerate(packets):
                    data += packet
            else:
                data = data[9:]
        except Exception as e:
            print(e)
            return False
        data = data[4:]

        header, data = self.__get_byte(data)
        num, data = self.__get_short(data)
        result = {}

        # Server sends incomplete packets. Ignore "NumPackets" value.
        while 1:
            try:
                rule_name, data = self.__get_string(data)
                rule_value, data = self.__get_string(data)
                if rule_value:
                    result[rule_name] = rule_value
            except Exception as e:
                break

        return result

    # <-------------------getRules() End ------------------------->

    def __get_byte(self, data):
        if self.is_third:
            return data[0], data[1:]
        else:
            return ord(data[0]), data[1:]

    def __get_short(self, data):
        return struct.unpack('<h', data[0:2])[0], data[2:]

    def __get_long(self, data):
        return struct.unpack('<l', data[0:4])[0], data[4:]

    def __get_long_long(self, data):
        return struct.unpack('<Q', data[0:8])[0], data[8:]

    def __get_float(self, data):
        return struct.unpack('<f', data[0:4])[0], data[4:]

    def __get_string(self, data):
        s = ""
        i = 0
        if not self.is_third:
            while data[i] != '\x00':
                s += data[i]
                i += 1
        else:
            while chr(data[i]) != '\x00':
                i += 1
            s = data[:i].decode()
        return s, data[i + 1:]
