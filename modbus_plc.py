__author__ = 'internat'


from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer
from twisted.internet.task import LoopingCall

import serial

import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.ERROR)

import sys, random

arduino_dev_port = "/dev/ttyUSB0"  # COM port on win
ser = serial.Serial(port=arduino_dev_port, baudrate=115200, bytesize=8, parity=serial.PARITY_NONE, stopbits=1)
listen_conf = ("192.168.0.104", 10503)



store = ModbusSlaveContext(
    di = ModbusSequentialDataBlock(0, [False]*20),
    co = ModbusSequentialDataBlock(0, [False]*20),
    hr = ModbusSequentialDataBlock(0, [3]*20),
    ir = ModbusSequentialDataBlock(0, [4]*20))



context = ModbusServerContext(slaves=store, single=True)


identity = ModbusDeviceIdentification()
identity.VendorName  = 'SCADALiaris'
identity.ProductCode = 'RealPLC 1'
identity.VendorUrl   = 'http://github.com/bashwork/pymodbus/'
identity.ProductName = 'pymodbus Server'
identity.ModelName   = 'pymodbus Server'
identity.MajorMinorRevision = 'v0.5'



def update_writer(a):

    slave_id = 1

    try:
        data_from_plc = ser.readline()


        proximity = int(data_from_plc.split(":")[0])
        light = int(data_from_plc.split(":")[1])
        button = int(data_from_plc.split(":")[2])

    except Exception as ex:
        print "EXCEPTION ", ex
        return

    print "GOT proximity" , str(proximity) , ": light" , str(light)

    context[slave_id].setValues(4, 1, [proximity])
    context[slave_id].setValues(4, 2, [light])

    context[slave_id].setValues(2, 1, [True if button == 1 else False])


    values = context[slave_id].getValues(4, 1, count=10)
    print "IR:", values, "(" + str(len(values)) + ")"

    output_registers = context[slave_id].getValues(3, 0, count=10)
    print "HR:" , output_registers

    input_coils = context[slave_id].getValues(2, 1, count=10)
    print "DI:" , input_coils

    output_coils = context[slave_id].getValues(1, 1, count=10)
    print "CO:" , output_coils

    data_to_plc = ["0", ":", "0", "\n"]
    if output_coils[0]:
        data_to_plc[0] = "1"

    if output_coils[1]:
        data_to_plc[2] = "1"

    ser.write(''.join(data_to_plc))

    print "_" * 100

time = 0.01 #2
loop = LoopingCall(f=update_writer,a=(context,))
loop.start(time, now=False)
StartTcpServer(context, identity=identity, address=listen_conf)

