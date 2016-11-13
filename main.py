__author__ = 'internat'


from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

from twisted.internet.task import LoopingCall

import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.ERROR)

import sys, random




store = ModbusSlaveContext(
    di = ModbusSequentialDataBlock(0, [1]*20),
    co = ModbusSequentialDataBlock(0, [False]*20),
    hr = ModbusSequentialDataBlock(0, [3]*20),
    ir = ModbusSequentialDataBlock(0, [4]*20))

context = ModbusServerContext(slaves=store, single=True)

identity = ModbusDeviceIdentification()
identity.VendorName  = 'pymodbus'
identity.ProductCode = 'PM'
identity.VendorUrl   = 'http://github.com/bashwork/pymodbus/'
identity.ProductName = 'pymodbus Server'
identity.ModelName   = 'pymodbus Server'
identity.MajorMinorRevision = '1.0'

i = 0

def update_writer(a):

    global i
    i += 1

    if i == 100:
        i = 0

    log.debug("updating context")
    context = a[0]
    register = 4 #random.randint(1,10)
    slave_id = 0x0
    # address = 0x00
    address = random.randint(0,10)

    value = list()
    value.append(random.randint(1,100))
    # print address, value[0]
    # values[1] = 20

    context[slave_id].setValues(4, address, value)


    ci_val = i % 2
    # print ci_val
    context[slave_id].setValues(2, 1, [ci_val])

    values = context[slave_id].getValues(4, 1, count=10)
    print "IR:", values, "(" + str(len(values)) + ")"

    output_registers = context[slave_id].getValues(3, 0, count=10)
    print "HR:" , output_registers

    input_coils = context[slave_id].getValues(1, 0, count=10)
    print "DI:" , input_coils

    output_coils = context[slave_id].getValues(2, 0, count=10)
    print "CO:" , output_coils


    print "_" * 100

time = 2
loop = LoopingCall(f=update_writer,a=(context,))
loop.start(time, now=False)
StartTcpServer(context, identity=identity, address=("192.168.0.104",10502))
