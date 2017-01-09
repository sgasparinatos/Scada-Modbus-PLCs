__author__ = 'internat'


from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer
from twisted.internet.task import LoopingCall
from argparse import ArgumentParser
from rpi_plc import Rpi1Wire

import serial
import random
import sys

import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.ERROR)

i=0





def rpi_plc(a):

    context = a[0]
    rpi = a[1]
    args = a[2]

    slave_id = 1

    data_from_plc = rpi.get_temps()




    if args.verbose:
        print "GOT proximity" , str(data_from_plc)









    values = context[slave_id].getValues(4, 1, count=10)
    i = 0
    for t in data_from_plc:
        context[slave_id].setValues(4, i+1, [data_from_plc[i]])
        i += 1

    output_registers = context[slave_id].getValues(3, 0, count=10)
    input_coils = context[slave_id].getValues(2, 1, count=10)
    output_coils = context[slave_id].getValues(1, 1, count=10)

    data_to_plc = ["0", ":", "0", "\n"]
    if output_coils[0]:
        data_to_plc[0] = "1"

    if output_coils[1]:
        data_to_plc[2] = "1"




    if args.verbose:
        print "IR:", values, "(" + str(len(values)) + ")"
        print "HR:" , output_registers
        print "DI:" , input_coils
        print "CO:" , output_coils

    print "_" * 100



def random_plc(a):

    global i
    i += 1

    if i == 100:
        i = 0

    log.debug("updating context")
    context = a[0]
    args = a[1]
    register = 4 #random.randint(1,10)
    slave_id = 0x0
    address = random.randint(0,10)

    value = list()
    value.append(random.randint(1,100))

    context[slave_id].setValues(4, address, value)


    ci_val = i % 2
    context[slave_id].setValues(2, 1, [ci_val])
    values = context[slave_id].getValues(4, 1, count=10)
    output_registers = context[slave_id].getValues(3, 0, count=10)
    input_coils = context[slave_id].getValues(1, 0, count=10)
    output_coils = context[slave_id].getValues(2, 0, count=10)


    if args.verbose:
        print "IR:", values, "(" + str(len(values)) + ")"
        print "HR:" , output_registers
        print "DI:" , input_coils
        print "CO:" , output_coils
        print "_" * 100



def arduino_plc(a):


    context = a[0]
    ser_port = a[1]
    args = a[2]

    slave_id = 1

    try:
        data_from_plc = ser_port.readline()


        proximity = int(data_from_plc.split(":")[0])
        light = int(data_from_plc.split(":")[1])
        button = int(data_from_plc.split(":")[2])
        temperature= float(data_from_plc.split(":")[3])
        humidity = float(data_from_plc.split(":")[4])

    except Exception as ex:
        print "EXCEPTION ", ex
        return

    if args.verbose:
        print "GOT proximity" , str(proximity) , ": light" , str(light)

    context[slave_id].setValues(4, 1, [proximity])
    context[slave_id].setValues(4, 2, [light])
    context[slave_id].setValues(4, 3, [temperature])
    context[slave_id].setValues(4, 4, [humidity])
    context[slave_id].setValues(2, 1, [True if button == 1 else False])


    values = context[slave_id].getValues(4, 1, count=10)
    output_registers = context[slave_id].getValues(3, 0, count=10)
    input_coils = context[slave_id].getValues(2, 1, count=10)
    output_coils = context[slave_id].getValues(1, 1, count=10)

    data_to_plc = ["0", ":", "0", "\n"]
    if output_coils[0]:
        data_to_plc[0] = "1"

    if output_coils[1]:
        data_to_plc[2] = "1"

    ser_port.write(''.join(data_to_plc))



    if args.verbose:
        print "IR:", values, "(" + str(len(values)) + ")"
        print "HR:" , output_registers
        print "DI:" , input_coils
        print "CO:" , output_coils

    print "_" * 100


def main():


    args = parse_settings()


    if args.verbose:
        print args


    # arduino_dev_port = "/dev/ttyUSB0"  # COM port on win
    # listen_conf = ("192.168.0.104", 10503)
    listen_conf = (args.listen_address, args.listen_port)


    store = ModbusSlaveContext(
        di = ModbusSequentialDataBlock(0, [False]*20),
        co = ModbusSequentialDataBlock(0, [False]*20),
        hr = ModbusSequentialDataBlock(0, [3]*20),
        ir = ModbusSequentialDataBlock(0, [4]*20))



    context = ModbusServerContext(slaves=store, single=True)


    identity = ModbusDeviceIdentification()
    identity.VendorName  = 'SCADALiaris'
    # identity.ProductCode = 'RealPLC 1'
    identity.VendorUrl   = 'http://github.com/bashwork/pymodbus/'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName   = 'pymodbus Server'
    identity.MajorMinorRevision = 'v0.5'


    time = args.poll_interval
    if not args.random :

        if args.rpi:
            rpi = Rpi1Wire()

            identity.ProductCode = 'RPiPLC 1'
            loop = LoopingCall(f=rpi_plc, a=(context, rpi, args))
            loop.start(time, now=False)
            StartTcpServer(context, identity=identity, address=listen_conf)

        else:

            try:
                serial_port = serial.Serial(port=args.serial_port, baudrate=115200, bytesize=8, parity=serial.PARITY_NONE, stopbits=1)
            except serial.SerialException as ex:
                print "ERROR", ex
                sys.exit(-1)
            identity.ProductCode = 'ArduinoPLC 1'
            loop = LoopingCall(f=arduino_plc,a=(context, serial_port, args))
            loop.start(time, now=False)
            StartTcpServer(context, identity=identity, address=listen_conf)



    else:
        identity.ProductCode = 'RandomPLC 1'
        loop = LoopingCall(f=random_plc, a=(context, args))
        loop.start(time, now=False)
        StartTcpServer(context, identity=identity, address=listen_conf)




def parse_settings():

    parser = ArgumentParser()
    parser.add_argument("-s", "--serial-port", help="Arduino serial port.", type=str, default="/dev/ttyUSB0")
    parser.add_argument("-p", "--listen-port", help="Tcp port to listen to.", type=int, default=10503)
    parser.add_argument("-a", "--listen-address", help="Listen ip address.", default="0.0.0.0", type=str)
    parser.add_argument("-i", "--poll-interval", help="Poll interval time in seconds",type=float, default=0.1 )
    parser.add_argument("-v", "--verbose", help="Prints the values of plc on stdout.", action="store_true", default=False)
    parser.add_argument("-r", "--random", help="Plc returns random values", action="store_true", default=False)
    parser.add_argument("--rpi", help="Plc returns random values", action="store_true", default=False)

    return parser.parse_args()


if __name__ == '__main__':
    main()