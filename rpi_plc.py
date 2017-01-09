__author__ = 'internat'
import time
import os
from threading import Thread


class Rpi1Wire():


    temp_sensor = '/sys/bus/w1/devices/28-00000863bada/w1_slave'

    w1_path = '/sys/bus/w1/devices/'
    sensors = list()
    temps = list()
    threads = list()
    interval = 1
    work = True

    def __init__(self):
        self.sensor_discovery()

        if len(self.sensors) > 0:
            i = 0
            for sensor_path in self.sensors:
                self.temps.append(0)
                t = Thread(target=self.read_thread, args=[sensor_path, i])
                t.start()
                self.threads = list()
                i += 1



    def stop(self):
        self.work = False



    def read_thread(self, sensor_path, id):


        print "GOT " , sensor_path, str(id)
        time.sleep(1)
        while self.work:
            self.temps[id] = self.read_temp(sensor_path)

            time.sleep(1)






    def sensor_discovery(self):
        dirs = os.listdir(self.w1_path)

        for dir in dirs:
            if dir.startswith("28-"):
                self.sensors.append(self.w1_path+dir+"/w1_slave")

        print "Found ", str(len(self.sensors))
        self.print_sensor_paths()


    def print_sensor_paths(self):

        i = 1
        for path in self.sensors:
            print str(i), path
            i += 1


    def temp_raw(self, path):

        f = open(path, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self, path):

        lines = self.temp_raw(path)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.temp_raw()

        temp_output = lines[1].find('t=')

        if temp_output != -1:
            temp_string = lines[1].strip()[temp_output+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c


    def read_all_sensors(self):

        for i in range(len(self.sensors)):
            print self.read_temp(i)

    def get_temps(self):
        return self.temps






def main():

    rpi = Rpi1Wire()
    # rpi.read_all_sensors()
    while True:
        print(rpi.get_temps())
        time.sleep(1)







if __name__ == '__main__':
    main()
