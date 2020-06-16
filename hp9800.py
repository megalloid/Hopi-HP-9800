#!/usr/bin/env python3

import serial
import binascii
import struct

from time import sleep

####################################################
#  Класс для работы с измерителем AC (Hopi HP-9800)
####################################################
class acmeter(object):

    REGS=[
            ("Active Power","W"),
            ("RMS Current","A"),
            ("Voltage RMS","V"),
            ("Frequency","Hz"),
            ("Power Factor","pf"),
            ("Annual Power","KWH"),
            ("Active Power","KWH"),
            ("Reactive Power","KWH"),
            ("Load Time","mins"),
        ]


    #####################################################################
    #   Инициализация последовательного порта, задаётся в начале программы
    #####################################################################
    def __init__(self, port):

        # Пытаемся открыть последовательный порт
        try:
            self.acmeter_serial = serial.Serial(port, baudrate = 9600, timeout = 1)
            print("INFO: Подключена управляемая розетка через последовательный порт {0} \n\r".format(port))
        
        except: # SerialException:
            print("ERROR: Проблема c подключением управляемой розетки: не могу открыть порт {0} \n\r".format(port))
            exit(1)


    #####################################################################
    #  Читаем указанный регистр 
    #####################################################################
    def readRegisters(self, first, count, address = 1):
        
        cmd = 0x03
        fout = []

        # Пакуем битовую массу для отправки и добавляем CRC
        measure_request = struct.pack(">BBHH", address, cmd, first, count)
        measure_request += self.crc(measure_request)

        # Отправляем запрос к устройству
        self.acmeter_serial.write(measure_request)

        replyLen = 3 + (count * 2) + 2

        reply = self.acmeter_serial.read(replyLen)

        if len(reply) != replyLen:
            print("ERROR: Ожидаемый размер ответа от управляемой розетки не совпадает с полученным. Ожидаемый:", replyLen, "Фактический: ", len(reply))
            return


        reply_crc = self.crc(reply[:-2])

        if reply_crc != reply[-2:]:
            print("ERROR: Ошибка контрольной суммы CRC от ответа управляемой розетки ")
            return
        
        # Распаковываем ответ в переменные
        address_reply, command_reply = struct.unpack(">BB", reply[:2])

        if (address_reply == address) and (command_reply == cmd):

            reply_double = reply[3:-2]

            fpos = 0
            while fpos < len(reply_double):

                fpval = reply_double[fpos:fpos+4]
                v = struct.unpack("<f", fpval)[0]
                fout.append(v)
                fpos += 4
            
            return fout

        else:
            print("ERROR: Bad reply from acmeter")


    #####################################################################
    # RMS Current
    #####################################################################
    def printCurrent(self):
        
        value = self.readRegisters(0, len(self.REGS) * 2)
        print("RMS Current: "+str(round(value[1], 3)))

    def getCurrent(self):
        
        value = self.readRegisters(0, len(self.REGS) * 2)
        return float(round(value[1], 3))

    
    #####################################################################
    # Voltage RMS
    #####################################################################
    def printVoltage(self):
        
        value = self.readRegisters(2, len(self.REGS) * 2)
        print("Voltage RMS: "+str(round(value[1], 1)))
 
    def getVoltage(self):
        
        value = self.readRegisters(2, len(self.REGS) * 2)
        return float(round(value[1], 1))


    #####################################################################
    # Frequency
    #####################################################################
    def printFrequency(self):
        
        value = self.readRegisters(4, len(self.REGS) * 2)
        print("Frequency: "+str(round(value[1], 2)))
 
    def getFrequency(self):
        
        value = self.readRegisters(4, len(self.REGS) * 2)
        return float(round(value[1], 2))


    #####################################################################
    # PowerFactor
    #####################################################################
    def printPowerFactor(self):
        
        value = self.readRegisters(6, len(self.REGS) * 2)
        print("PowerFactor: "+str(round(value[1], 4)))
 

    def getPowerFactor(self):
        
        value = self.readRegisters(6, len(self.REGS) * 2)
        return float(round(value[1], 4))

    
    #####################################################################
    # Annual PowerConsumption (kWH)
    #####################################################################
    def printAnnualPowerConsumption(self):
        
        value = self.readRegisters(8, len(self.REGS) * 2)
        print("AnnualPowerConsumption (kWH): "+str(round(value[1], 2)))

    def getAnnualPowerConsumption(self):
        
        value = self.readRegisters(8, len(self.REGS) * 2)
        return float(round(value[1], 2))


    #####################################################################
    # Reactive Power (kWH)
    #####################################################################
    def printReactivePower(self):
        
        value = self.readRegisters(14, len(self.REGS) * 2)
        print("Reactive Power (kWH): "+str(round(value[0], 3)))

    def getReactivePower(self):
        
        value = self.readRegisters(14, len(self.REGS) * 2)
        return float(round(value[0], 3))


    #####################################################################
    # Active time (seconds)
    #####################################################################
    def printUptime(self):
        
        value = self.readRegisters(16, len(self.REGS) * 2)
        print("Load time (seconds): "+str(round(value[0], 3)))

    def getUptime(self):
        
        value = self.readRegisters(16, len(self.REGS) * 2)
        return float(round(value[0], 3))

    
    #####################################################################
    # Active power
    #####################################################################
    def printPower(self):
        
        value = self.readRegisters(0, len(self.REGS) * 2)
        print("Active Power (W): "+str(round(value[0], 3)))

    def getPower(self):
        
        value = self.readRegisters(0, len(self.REGS) * 2)
        return float(round(value[0], 3))


    #####################################################################
    #   Функция вычисления контрольной суммы
    #####################################################################
    def crc(self, data):

        poly = 0xA001
        crc = 0xFFFF

        for b in data:

            cur_byte = 0xFF & ord(chr(b))

            for _ in range(0, 8):
                if (crc & 0x0001) ^ (cur_byte & 0x0001):
                    crc = (crc >> 1) ^ poly
                else:
                    crc >>= 1
                cur_byte >>= 1

        return struct.pack("<H", crc & 0xFFFF)



    
