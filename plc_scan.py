__author__ = 'internat'


from pymodbus.mei_message import ReadDeviceInformationRequest
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Defaults
import sys
import progressbar
import time
import argparse


upload_data = False
# search_range = "100-110"
search_range = "1-30"
subnet = "192.168.43."
# ports = "503,502,10503"
ports = '10503'

output = ""
total_found = 0
Defaults.Timeout = 0.5


def print_info(info, ip):

    global output

    margin = 8

    # print 30 * "-"
    # print str("Summary : " + ip).center(30)
    # print 30 * "-"
    #
    # print str("Vendor".ljust(margin) + " : " + info[0])
    # print str("Model".ljust(margin) + " : " +  info[1])
    # print str("Version".ljust(margin)+ " : "+  info[2])

    output += 30 * "-" + "\n"
    output += str("Summary : " + ip).center(30) + "\n"
    output += 30 * "-" + "\n"

    output += str("Vendor".ljust(margin) + " : " + info[0]) + "\n"
    output += str("Model".ljust(margin) + " : " +  info[1]) + "\n"
    output += str("Version".ljust(margin)+ " : "+  info[2]) + "\n"




def dump_plc():
    pass


def upload_plc_data():
    pass

def access_plc(ip, port):

    global total_found

    try:
        client = ModbusTcpClient(ip, port=port)
        req = ReadDeviceInformationRequest()
        resp = client.execute(req)
        print_info(resp.information, ip + ":" + str(port))
        total_found += 1

    except Exception as ex:
        return



# def parse_arguments():






def main():

    global total_found

    low_limit, high_limit = search_range.split("-")
    max_val = (int(high_limit)+1 - int(low_limit)) * len(ports.split(","))
    bar_counter = 0

    bar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.Bar("=",'[',']'), ' ', progressbar.Percentage()])
    # print "Scanning for tcp/modbus devices"
    bar.start()


    for ip in range(int(low_limit), int(high_limit)+1):
        for port in ports.split(","):
            bar_counter += 1
            access_plc(subnet+ str(ip), int(port))
            bar.update(int((bar_counter * 100)/max_val))


    bar.finish()

    time.sleep(1)
    print "Total Modbus devices found : ", str(total_found)
    print
    print
    print output

if __name__ == '__main__':
    main()
