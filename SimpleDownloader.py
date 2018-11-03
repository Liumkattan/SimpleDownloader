#! /usr/bin/python3

"""Python Fast Downloader
	A script thats split files and download them smaltinuasly"""

import os, time, sys
import requests as req
from queue import Queue
from threading import Thread

# Default Values
tool_version 	= "0.1.1"
byte_size 		= 1048576
max_threads 	= 5
max_retry 		= 5
default_path 	= os.path.join(os.environ["HOME"], 'Videos', 'SimpleDownloader')
footer_size 	= 22 # The size of the data proves the file was downloaded by this script
footer_indicator = "fuz_file"

# Base directory insurance
if not os.path.exists(default_path): os.mkdir(default_path)

class File(object):
	"""docstring for File
		A calss handles the information about the desired file"""
	def __init__(self, url=None, location=default_path, name=None):
		self.url 		= 'http://'+url if url and 'http' not in url else url 
		self.name 		= self.url.split("/")[-1] if url and not name else name 
		self._name 		= name
		self.location 	= location if os.path.isfile(location) or not self.name else os.path.join(location, self.name)
		self.name 		= self.location.split("/")[-1] if not self.name else self.name
		self.exists 	= self.check_existance()
		self.online 	= self.grab_data()


	def grab_data(self):
		if self.url:
			try:
				with req.get(self.url, stream=True) as con:
					if "Accept-Ranges" in con.headers:
						self.accept_range = True
					else: self.accept_range = False # Check status_code for 206
					self.size = int(con.headers['Content-length'])
					self.type = con.headers['Content-Type'].split("/")[0]
					return True
			except req.exceptions.ConnectionError as err:
				if self.exists:
					return False
				raise Exception("Check your internet connection.")
				exit()
		self.size = None
		self.online = False
		self.accept_range = False
		self.type = 'unknown'
		return False

	def check_existance(self):
		if os.path.exists(self.location) and os.path.isfile(self.location):
			self.local_size = os.path.getsize(self.location)
			return True
		else:
			if not self.url:
				raise Exception("No downloading resorce, please enter one at least: \n- old inturupted download \n- file url")
				exit()
			return False

	def __str__(self):
		if self.size:
			return  f"{self.type} > {self.name} ({round(float(self.size)/byte_size, 2)}MB)"
		else: return f"Downloading {self.name}..."

class Download(object):
	"""docstring for Download
		A Class handles Downloading and ensure the file"""
	time_start			= time.time()
	def __init__(self, file, threads=max_threads,
					path=default_path, retries=max_retry, verbos=True, split=True):
		self.file 				= file
		self.path 				= path
		self.split 				= split
		self.verbos 			= verbos
		self.retries 			= retries
		self.download_location 	= os.path.join(self.path, self.file.name)
		self.threads_number 	= threads
		self.incompelet 		= []
		self.threads 			= []
		self.progress_list		= []
		self.session 			= req.Session()
		self.chunk_list 		= Queue()
		self.order_list 		= Queue()
		self._extention			= "fuz"
		self.__mine				= self._check_my_download()
		self.chunk_size 		= int(self.file.size / len(str(self.file.size)))
		self.divisior 			= int(self.file.size / self.chunk_size)

		if self.file.size % self.chunk_size != 0:
				self.divisior = int(self.file.size / self.chunk_size) + 1

	def _check_my_download(self): # Check the footer of the file
		try:
			if self.file.exists or os.path.exists(".".join([self.file.location, self._extention])):
				if not self.file.exists:
					self.file.location = ".".join([self.file.location, self._extention])
					self.file.local_size = os.path.getsize(self.file.location)
				with open(self.file.location, 'rb') as data:
					data.seek(self.file.local_size - footer_size)
					self.__footer = data.read(footer_size).decode()
				if footer_indicator in self.__footer:
					old_size = int(self.__footer.split(" ")[-1])
					
					if self.file.size:
						if self.file.size != old_size:
							raise Exception("The file in the url given is not the same as local file.")
							exit()
					else: self.file.size = old_size
					
					if self.file.location.split('.')[-1] != self._extention:
						loc = ".".join([self.file.location, self._extention])
						os.rename(self.file.location, loc)
						self.file.location = loc

					return True
				else:
					if not self.file.online:
						raise Exception("File is not supported and no given url.")
						exit()
					return False
		except UnicodeDecodeError:
			raise Exception(f"File Exists: the file {self.file.name} is already there {self.file.location}.")


	def chunck_distreputer(self): # Devide file size to chunks and loop count
		beg = 0
		if self.split:
			if self.incompelet:
				for chunk in range(len(self.incompelet)):
					self.chunk_list.put(self.incompelet[chunk])
					self.order_list.put(chunk)
			else:
				self.chunk_list.put(beg)
				for chunk in range(self.divisior):
					if beg < self.file.size:
						beg += self.chunk_size
						self.chunk_list.put(beg)
						self.order_list.put(chunk)
			self.thread_executer()
		else:
			if self.verbos:
				print("File Splitting is turnned off...")
			self.normal_download()

	def normal_download(self): # Downloading Chunks one-by-one
		payload = self.session.get(self.file.url, stream=True)
		with open(self.file.location, 'wb') as fil:
			for chunk in payload.iter_content(chunk_size=self.chunk_size):
				numb = self.progress_list[-1] if self.progress_list else 0
				self.progress(self.chunk_size + numb)
				if chunk: fil.write(chunk)


	def get_chunck(self, start_byte, end_byte): # Grabbing single chunk
		assert start_byte < end_byte
		assert start_byte < self.file.size
		if end_byte > self.file.size: end_byte = self.file.size
		byts = "bytes={0}-{1}".format(start_byte, end_byte)
		for i in range(self.retries):
			try:
				chunk = self.session.get(self.file.url, headers={"Range": byts}, stream=True)
				if chunk.status_code == 206: return chunk.content
			except Exception as err:
				print(f"Error: Could not download Chunk {start_byte}-{end_byte}", ", Retrying..." if i < self.retries-1 else "!")

		

	def chunk_collector(self): # prepering for downloading chunk & writing data off
		try:
			while not self.order_list.empty():
				order 	= self.order_list.get()
				start 	= self.chunk_list.get()
				end 	= start + self.chunk_size - 1
				payload = self.get_chunck(start, end)
				with open(self.file.location, 'r+b') as writer:
					writer.seek(start)
					writer.write(payload)
					self.progress(str(start))

					writer.seek(0, 0)
					writer.seek(self.file.size + 1)
					writer.write(f"{self.file.url};{self.file.name}|{';'.join(self.progress_list)}|fuz_file {self.file.size}".encode())
		except KeyboardInterrupt:
			print(" Closing...")
			exit()

	def thread_executer(self): # Executing threades according to max_threads
		threads_needed = self.threads_number
		if self.threads_number > self.divisior:
			threads_needed = self.divisior

		for th in range(threads_needed):
			t = Thread(target=self.chunk_collector)
			t.start()
			self.threads.append(t)

	def wait_until(self, var1, var2, timeout=0, period=0.25): # waits for certain condition
		wait = True
		mustend = time.time() + timeout
		while wait:
			if timeout != 0 and time.time() > mustend: wait = False
			if var1 in var2: return True
			time.sleep(period)
		return False

	def collect_data(self):
		beg = 0
		with open(self.file.location, 'rb') as fi: # Read Text
			fi.seek(self.file.size + 1)
			data = fi.read().decode().split("|")

		old_url, old_name = data[0].split(';')
		dones = data[1].split(';')
		for i in range(int(self.file.size/self.chunk_size)+1):
			if beg < self.file.size:
				if str(beg) not in dones:
					self.incompelet.append(beg)
				beg+= self.chunk_size
		self.divisior = len(self.incompelet)

		if self.file.online:
			if not self.file._name:
				self.file.name = old_name
		else:
			self.file.url = str(old_url)
			self.file.online = self.file.grab_data()



	def collect_file(self): # Collecting downloaded data to one file
		if self.verbos:
			print("Collecting Downloaded Data...")
		if self.download_location.split('.')[-1] == self._extention:
			self.download_location = self.download_location.replace('.'+self._extention, '')
		with open(self.file.location,"rb") as inp: # ger video data only
			file_data = inp.read(self.file.size)

		with open(self.download_location, 'wb') as out: # Writes the video out
			out.write(file_data)

		os.remove(self.file.location)


	def progress(self, start): # Recording progress& displaying
		self.progress_list.append(start)
		prec = round((len(self.progress_list)/(self.divisior))*100)
		if self.verbos:
			print(f"Downloading... {prec}%")
		if prec == 100:
			self.collect_file()
			if self.verbos:
				print("Downloaded in: {} Sec".format(round(time.time() - self.time_start, 2)))


	def download(self, auto=True): # arranging and starting events
		try:
			if self.__mine:
				self.collect_data()
			else:
				if self.verbos:
					print(self.file)
				if self.file.location.split('.')[-1] != self._extention:
					self.file.location = ".".join([self.file.location, self._extention])
				with open(self.file.location,"wb") as f:
					f.seek(self.file.size-1)
					f.write(b'\0')

			if self.file.online:
				status = self.session.get(self.file.url, 
								headers={"Range": "bytes=0-1"}, stream=True).status_code

				if (not self.file.accept_range and status != 206):
					if self.verbos:
						print("Server Doesn't Support File Splitting...")
					self.split = False

				self.chunck_distreputer()
			else: raise Exception("url given is not working.")
		except KeyboardInterrupt:
			print(" Closing...")
			exit()

def main():
	from argparse import ArgumentParser

	parser = ArgumentParser()
	parser.add_argument("-u", "--url", help="URL of the file to download")
	parser.add_argument("-l", "--location", help="location of the file on machine") # besides --download-location to change file location after downloading
	parser.add_argument("-n", "--name", help="Optional Custom name")
	parser.add_argument("-p", "--path", help="Change download directory path, Default: " + default_path)
	parser.add_argument("-r", "--retry", help="Set number of retrie, default is " + str(max_retry))
	parser.add_argument("-s", "--no-split", action="store_true", help="Disable default file splitting behavior")
	parser.add_argument("-t", "--threads", help="Maximum number of threads to use (Working only if split is avilable)")
	parser.add_argument("-v", "--no-verbos", action="store_true", help="Disable verbosity (Do not display output), default is Displaying")
	parser.add_argument("-V", "--version", action="store_true", help="Display tool version and exit")


	args 		= parser.parse_args()
	split 		= False if args.no_split else True
	verbos 		= False if args.no_verbos else True 
	path 		= args.path if args.path else default_path
	location 	= args.location if args.location else default_path
	threads 	= args.threads if args.threads else max_threads
	retries 	= args.retry if args.retry else max_retry

	if args.version:
		print("SimpleDownloader:", tool_version)
		exit()

	if len(sys.argv) > 1:
		Download(File(url=args.url, location=location, name=args.name),
					threads=threads, path=path, retries=retries,
					verbos=verbos, split=split).download()
	else: parser.print_help(sys.stderr) 

if __name__ == '__main__':
	main()

