# This program downloads the last page uploaded to the TwoKinds website (twokinds.keenspot.com)

import requests, time, hashlib, os, urllib, threading, json, twitter
from bs4 import BeautifulSoup as BS
#why is this even a thing?
from datetime import datetime

## used to keep track elapsed time
start_time=datetime.now().replace(microsecond=0).replace(microsecond=0)
# default sleep_time
sleep_time=45
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

def hash_download(file):
	pagehash = hashlib.md5()
	while True:
		data = file.read()
		if not data:
			break
		pagehash.update(data)
	return pagehash.hexdigest()

def errormessage(e):
	if "Errno 10060" in e:
		print ("[ERROR: 10060] Unable to connect to twokinds.keenspot.com")
	elif "Errno 11001" in e:
		print ("[ERROR: 11001] Unable to connect to twokinds.keenspot.com")
	else:
	    print(e)
# commands that can be passe dinto the program
'''
help: lists all the commands
runtime: checks how long the program has been running
checknow: immediately checks if an update has been made (if you are impatient like me and don't like to wait)
'''
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
			errormessage(str(e))

## renames the file if it already exists
def rename_if_file_exists (file_dir, file_name):
	i=1
	name=file_name.split('.')[0]
	while True:
		if os.path.isfile(file_dir+file_name):
			file_name=file_name.split('.')
			file_name[0]=name+' ('+str(i)+')'
			file_name='.'.join(file_name)
		else:
			break
		i+=1
	return file_name	
def remove_temp():
	global tkpath
	temp=tkpath+'temp'
	if os.path.isfile (temp):
		os.remove(temp) 

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
			errormessage(str(e))
		except Exception as e:
			errormessage(str(e))
		else: 
			html = response.read().decode()
			response.close()
			soup = BS(html, "html.parser")
			latestimage = []
			for images in soup.find_all('img'):
				if 'http://cdn.twokinds.keenspot.com/comics/' in images['src']:
					latestimage.append(images['src'])
					

			for images in latestimage:
				imagename = images.split('/')[-1]
				try:
				    pagedownloader = opener.open(images)
				except urllib.error.HTTPError as e:
					errormessage("urllib error:\t"+str(e))
				except Exception as e:
					errormessage(str(e))
				else:
					temphash = hash_download(opener.open(images))
					
					if temphash not in hashtable:
						imagename= rename_if_file_exists (tkpath, imagename)
						downloadedimage = open(tkpath+imagename, 'wb')
						downloadedimage.write(pagedownloader.read())
						downloadedimage.close()
						hashtable.append(hash_file(tkpath+imagename))
						print ('\n\nNew page found! Adding ', imagename, ' to the database.\nFile Name:\t',	imagename, '\nHash:\t\t', temphash)

					else:
						if status:
							os.remove(temp)
							print ('No update found\n')
					pagedownloader.close()
		if loop and running:
			i=0
			while i < get_sleep_time() and running:
				time.sleep(1)
				i+=1
		else:
			break
# retweets the latest comic
def retweet_latest_comic():
	while True:
		try:
			# You must define your own keys and tokens
			consumer_key=""
			consumer_secret=""
			access_token_key=""
			access_token_secret=""

			api = twitter.Api(consumer_key=consumer_key,
			                      consumer_secret=consumer_secret,
			                      access_token_key=access_token_key,
			                      access_token_secret=access_token_secret,
			                      sleep_on_rate_limit=True)
			comictweets=[]
			favorites=api.GetFavorites(user_id=None, screen_name='Hyginx', count=100, since_id=None, max_id=None, include_entities=True, return_json=False) 
			# print ("Rate Limit = "+str(api.InitializeRateLimit()))
			statuses = api.GetUserTimeline(screen_name="TwoKinds", exclude_replies=True)
			for s in api.GetUserTimeline(screen_name="TwoKinds", exclude_replies=True):
				# Tom follows a very specific format for his posts, which makes my job a hell of a lot easier. Thanks, Tom!
				if ("[Comic][" in s.text):
					comictweets.append(s.text)\
					# if the update has not been retweeted
					if (not s.retweeted):
						api.PostRetweet(s.id, trim_user=False)
						print ("Retweeted Comic update!\n"+comictweets[0])
					#Favorites the tweet because if it's worth retweeting, it's worth favoriting
					if (s not in favorites):
						try:
							api.CreateFavorite(status=s, status_id=s.id, include_entities=True)
							print ('Favorited'+s.text.encode('ascii', 'ignore').decode('unicode_escape'))
						except Exception as e:
							if ('You have already favorited this status.' not in str(e)):
								raise e
			time.sleep(60)
		except Exception as e:
			raise e

def main():
	inputthread=threading.Thread(target=read_input)
	inputthread.start()
	twitterthread=threading.Thread(target=retweet_latest_comic)
	twitterthread.start()
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
