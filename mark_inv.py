import time
import os
import mysql.connector
import subprocess
from threading import Thread

HOST = "Zabbix_hostname"
ZabS = "Zabbix_server_ip"

def connect():
    try:
        conn = mysql.connector.connect(host='localhost',
                                       database='Some_Zabbix_DB',
                                       user='selectuser',
                                       password='Some_password')
        if conn.is_connected():
	    cursor = conn.cursor()
	    cursor.execute("select hosts.name,interface.ip from hosts LEFT OUTER JOIN interface ON hosts.hostid=interface.hostid where hosts.status = 0 AND interface.ip NOT IN ('NULL', '127.0.0.1') AND (hosts.available = !0 OR hosts.ipmi_available != 0 OR hosts.snmp_available != 0) group by interface.ip order by hosts.name;")
	    row = cursor.fetchall()
	    return row
    except Error as e:
        print(e)
    finally:
	conn.close()

def create_items():
	for item in SQL_output:
		acc = "{0}_{1}".format(item[0],item[1])
	        pipe = os.popen('zabbix_sender -z {0}  -s {1} -k host.finder -o \'{{"data":[{{"{{#NR}}":"{2}"}}]}}\''.format(ZabS,HOST,acc))
		time.sleep(1)

def ping(item):
	pipe = os.popen('ping -c 10 {0}'.format(item[1]))

def avail_check(item):
	ping_output = subprocess.call(['ping', '-c', '1', item[1]])
	return ping_output

def tcpdump(item):
	output = os.popen('/sbin/tcpdump -i any -s0 -v -c 1 src {0}'.format(item[1])).read()
	output = output.split('(')[1].split(',')[0]
	return output

class ThreadWithReturnValue(Thread):
	def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        	Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        	self._return = None
	def run(self):
		if self._Thread__target is not None:
			self._return = self._Thread__target(*self._Thread__args,**self._Thread__kwargs)
	def join(self):
		Thread.join(self)
		return self._return

def main():
	try:
		for item in SQL_output:
			acc = "{0}_{1}".format(item[0],item[1])
			ping_output = avail_check(item)
                        if ping_output == 0:
				thread1 = Thread(target=ping, args=(item,))
				thread2 = ThreadWithReturnValue(target=tcpdump, args=(item,))
				thread1.start()
				thread2.start()
				thread1.join()
				time.sleep(1)
				output = thread2.join()
        	        	pipe = os.popen('zabbix_sender -z {0} -s {1} -k \'host_[{2}]\' -o "{3}"'.format(ZabS,HOST,acc,output))
			else:
                                pipe = os.popen('zabbix_sender -z {0} -s {1} -k \'host_[{2}]\' -o "No ping"'.format(ZabS,HOST,acc))
	except Error as e:
	        print(e)

if __name__ == '__main__':
	SQL_output = connect()
	create_items()
	time.sleep(30)
	main()
