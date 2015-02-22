#!/usr/bin/python

from lxml import etree
import urllib2
import ConfigParser
from datetime import datetime
import time
import pynotify
import os
from threading import Thread
from operator import itemgetter

FILEPATH = os.path.dirname(os.path.abspath(__file__))

def notify(header,text,color):
	pynotify.init('Codechef Alert')
	imageURI = 'file://' + FILEPATH + '/icons/'+color+'chef.jpeg'
	n = pynotify.Notification(header,text, imageURI)
	n.show()


def get_codechef_source():
	url = 'http://www.codechef.com/contests/'
	r = urllib2.urlopen(url)
	return r.read()


def get_datetime_object(datetime_string):
	return datetime.strptime(datetime_string,'%Y-%m-%d %H:%M:%S')



def write_contest_config():                  
	try:
		codechef_source = get_codechef_source()
		x = etree.HTML(codechef_source)            

		k = x.xpath("//div[@class='content-wrapper']/div[@id='statusdiv']/table/tbody/tr/td")
		l = x.xpath("//div[@class='content-wrapper']/div[@id='statusdiv']/table/tbody/tr/td/a")  

		contest_name = [ i.text for i in l ]                          
		contest =[ i.text for i in k if i.text is not None ]        
		if len(contest) == 0:
			raise Exception('Contest Page is Down')
		config = ConfigParser.RawConfigParser()
		config.add_section('STATS')                                                             
		config.set('STATS','last_update',datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S"))  # sets last fetch date and time
	
	
		for i in range(0,len(contest),3):
			if get_datetime_object(contest[i+2])>datetime.now():     # check for the Present or Future Contests
				config.add_section(contest[i])                                          # add contest ID as Section
				config.set(contest[i],'name',contest_name[i/3])                        #  set contest name
				config.set(contest[i],'start_date_time',contest[i+1])                  # set contest starting date and time
				config.set(contest[i],'end_date_time',contest[i+2])                    # set contest ending date and time
			
		with open(FILEPATH+'/contests.cfg', 'wb') as configfile:                                 # write contests to cfg file.           
			config.write(configfile)
	except:
		time.sleep(360)                      # sleep due to internet problems or site is down
		write_contest_config()


def get_config_update_date():
	config = ConfigParser.RawConfigParser()
	config.read(FILEPATH+'/contests.cfg')
	return get_datetime_object(config.get('STATS','last_update'))
	
	
	
def read_contest_config():
	config = ConfigParser.RawConfigParser()
	config.read(FILEPATH+'/contests.cfg')
	contests = []
	for i in config.sections()[len(config.sections())-1:0:-1]:
		s = None
		e = None
		if config.get(i,'start_date_time')!='Done':
			if get_datetime_object(config.get(i,'start_date_time')).date()==datetime.now().date() or get_datetime_object(config.get(i,'start_date_time')).date()==datetime.now().date().replace(day = datetime.now().date().day + 1):
				s = get_datetime_object(config.get(i,'start_date_time'))
		
		if config.get(i,'end_date_time')!='Done':
			if get_datetime_object(config.get(i,'end_date_time')).date()==datetime.now().date() or get_datetime_object(config.get(i,'end_date_time')).date()==datetime.now().date().replace(day = datetime.now().date().day + 1):
				e = get_datetime_object(config.get(i,'end_date_time'))
		
		if s!=None or e!=None:
			contests.append((i,config.get(i,'name'),s,e))

	return contests		
									


def notifier():
	while 1:
		contests = [(i[0],i[1],'start_date_time',i[2]) for i in read_contest_config() if i[2] is not None and i[2]>=datetime.now()] + [(i[0],i[1],'end_date_time',i[3]) for i in read_contest_config() if i[3] is not None and i[3]>=datetime.now()]
		if len(contests) == 0:
			time.sleep(3600)
		upcoming = min(contests,key = itemgetter(3))
		print "is sleeping for",(upcoming[3] -datetime.now()).seconds," seconds"
		time.sleep((upcoming[3] -datetime.now()).seconds)
		flag = 1
		while flag:
			if datetime.now()>=upcoming[3] and upcoming[2]=='start_date_time':
				notify(upcoming[1],"has Started","green")
				flag = 0
			if datetime.now()>=upcoming[3] and upcoming[2]=='end_date_time':
				notify(upcoming[1],"is Finished","red")
				flag = 0

def contest_config_updater():
	while 1:
		if (datetime.now() - get_config_update_date()).seconds //3600 >=6:
			write_contest_config()
			print "writting"
			
		else:
			print "sleeping updater"
			time.sleep(3600)
			
if __name__ == "__main__":
	#write_contest_config()
	Thread(target=contest_config_updater,args=()).start()
	notifier()
	
		
	
	
	



		



		
			
			
	

