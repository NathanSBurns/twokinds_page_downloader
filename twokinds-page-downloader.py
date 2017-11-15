# This program downloads the last page uploaded to the TwoKinds website (twokinds.keenspot.com)

import requests, time, hashlib, sys, os, urllib, threading
from bs4 import BeautifulSoup as BS
#why is this even a thing?
from datetime import datetime

## used to keep track elapsed time
start_time=datetime.now().replace(microsecond=0).replace(microsecond=0)
# default sleep_time
sleep_time=300
#used for ending threads
running=True

def get_sleep_time():
	return sleep_time

def set_sleep_time(seconds):
	try:
		global sleep_time
		sleep_time = int(seconds)
	except Exception as e:
		print ('please enter a digit number')

def set_running(tf):
	global running
	running = tf

## hashes files 
def hash_file(path):
	## buffer size for readin in files (64kb chunks)
	BUF_SIZE = 65536
	pagehash = hashlib.md5()
	with open(path, "rb") as p:
		while True:
			data = p.read(BUF_SIZE)
			if not data:
				break
			pagehash.update(data)
	p.close()
	return pagehash.hexdigest()

# commands that can be passe dinto the program
def read_input():
	while running:
		try:
			command=input('\nType "help" for list of commands.\n')
			if command.lower().strip() == 'help':
				print('List of commands:\n',
					'runtime: lists how long the program has been running.\n',
					'setsleeptime: set the time intervalk at which the script checks for updates (seconds)\n',
					'exit: exits the program',
					'checknow: checks if the comic has been udated.\n')
			elif command.lower() == 'runtime':
				print (datetime.now().replace(microsecond=0)-start_time)
			elif command.lower() == 'checknow':
				check_for_updates(True, False)
			elif command.lower() == 'exit':
				print ('exiting program')
				set_running(False)
				quit()
			elif command.lower() == 'setsleeptime':
				seconds=input("Enter number of seconds: ")
				set_sleep_time(seconds)
			else:
				print ('command "', command, '" not recognized')
		except Exception as e:
			print (e)

## renames the file if it already exists
def rename_if_file_exists (file_dir, file_name):
	i=1
	name=file_name.split('.')[0]
	while True:
		if os.path.isfile(file_dir+file_name):
			file_name=file_name.split('.')
			file_name[0]=name+' ('+str(i)+')'
			file_name='.'.join(file_name)
			# break
		else:
			break
		i+=1
	return file_name	

# status: Boolean. True prints updates, False displays nothing
# loop: Boolean describing whether or not updates will loop
def check_for_updates(status, loop):
	while True:
		if status:
			print ("\nChecking for updates")
		url = 'http://twokinds.keenspot.com/'

		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
		user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'
		opener.addheaders = [('user-agent', user_agent)]

		try:
		    response = opener.open(url)
		except urllib.error.HTTPError as e:
		    print(e)
		except Exception as e:
		    print(e)
		else: 
			html = response.read().decode()
			response.close()
			soup = BS(html, "html.parser")
			for classes in soup.find_all('class'):
				print (classes)
			for images in soup.find_all('img'):
				if 'http://cdn.twokinds.keenspot.com/comics/' in images['src']:
					
					latestimage = images['src']
					imagename = latestimage.split('/')[-1]
					

					'''# for trouble shooting and visual aid
					print('latest image: ', latestimage)
					print ('image name: ', imagename)'''

			try:
			    pagedownloader = opener.open(latestimage)
			except urllib.error.HTTPError as e:
			    print(e)
			except Exception as e:
			    print(e)
			else:
				temp = tkpath+'temp'
				downloadedimage = open(temp, 'wb')
				downloadedimage.write(pagedownloader.read())
				downloadedimage.close()

				# hash of the temp file
				temphash = hash_file(temp)
				# print ('latest hash:\t', temphash)
				
				if temphash not in hashtable:
					imagename= rename_if_file_exists (tkpath, imagename)
					os.rename(temp, tkpath+imagename)
					hashtable.append(hash_file(tkpath+imagename))
					print ('\n\nNew page found! Adding ', imagename, ' to the database.\nFile Name:\t',	imagename, '\nHash:\t\t', temphash)

				else:
					if status:
						print ('No update found\n')
				
				# usually the temp file should not be present. However, if the program was executed after the latest 
				# page was downloaded, the temp file will still be created 
				if os.path.isfile (temp):
					os.remove(temp)
				pagedownloader.close()
		if loop and running:
			i=0
			while i < get_sleep_time() and running:
				time.sleep(1)
				i+=1
		else:
			break
def main():
	inputthread=threading.Thread(target=read_input)
	inputthread.start()
	check_for_updates(False, True)

hashtable = []

## hashes all the known files and pushes them into n Array. This runs every time the program is executed but not as it is running. A seperate process will add new file hashes to the array
tkpath = "D:/Users/Hyginx/Pictures/TwoKinds/"
# tkpath=input("Path: ")
print ('hashing files')
for dirs, subdirs, files in os.walk(tkpath):
	for page in files:
		filepath = os.path.join(os.path.abspath(dirs), page)
		if '.jpg' in filepath or '.png' in filepath:
			hashtable.append(hash_file(filepath))
main()
