#! /usr/bin/python3

"""Python Fast Downloader
	A script split files and download them smaltinuasly"""

import os, time
import requests as req
from queue import Queue
from threading import Thread

# Default Values
byte_size = 1048576
max_threads 	= 5
max_retry 		= 5
default_path 	= os.path.join(os.environ["HOME"], 'Videos', 'PyDownloader')

class File(object):
	"""docstring for File
		A calss handles the information about the desired file"""
	def __init__(self, url=None, location=default_path, name=None):
		self.url = url
		self.name = name if name else self.url.split("/")[-1]
		try:
			with req.get(url, stream=True) as con:
				if "Accept-Ranges" in con.headers:
					self.accept_range = True
				else: self.accept_range = False # Check status_code for 206
				self.size = int(con.headers['Content-length'])
				self.type = con.headers['Content-Type'].split("/")[0]
		except req.exceptions.ConnectionError:
			raise req.exceptions.ConnectionError("Check your internet connection.")

	def __str__(self):
		return  "{} > {} ({}MB)".format(self.type, self.name, round(float(self.size)/byte_size, 2))



class Download(object):
	"""docstring for Download
		A Class handles Downloading and ensure the file"""
	time_start = time.time()
	def __init__(self, file, threads=max_threads, path=default_path, retries=max_retry, split=True):
		self.file 			= file
		self.path 			= path
		self.split 			= split
		self._extention		= ".fuz_part"
		self.location 		= os.path.join(self.path, self.file.name)
		self.time_start		= time.time()
		self.threads_number = threads
		self.threads 		= []
		self.progress_list	= []
		self.session 		= req.Session()
		self.chunk_list 	= Queue()
		self.order_list 	= Queue()
		self.chunk_size 	= int(self.file.size / len(str(self.file.size)))
		self.divisior 		= int(self.file.size / self.chunk_size)

	def chunck_distreputer(self):
		beg = 0
		if self.file.size % self.chunk_size != 0:
				self.divisior = int(self.file.size / self.chunk_size) + 1

		if self.split:
			self.chunk_list.put(beg)
			for chunk in range(self.divisior):
				if beg < self.file.size:
					beg += self.chunk_size
					self.chunk_list.put(beg)
					self.order_list.put(chunk)
			self.thread_executer()
		else:
			print("File Splitting is turnned off...")
			self.normal_download()

	def normal_download(self):
		num = 0
		payload = self.session.get(self.file.url, stream=True)
		with open(self.location+self._extention, 'wb') as fil:
			for chunk in payload.iter_content(chunk_size=self.chunk_size):
				self.progress(num)
				num+=1
				if chunk: fil.write(chunk)


	def get_chunck(self, start_byte, end_byte):
		assert start_byte < end_byte
		assert start_byte < self.file.size
		if end_byte > self.file.size: end_byte = self.file.size
		byts = "bytes={0}-{1}".format(start_byte, end_byte)
		return self.session.get(self.file.url, headers={"Range": byts}, stream=True).content
		

	def chunk_collector(self):

		while not self.order_list.empty():
			order 	= self.order_list.get()
			start 	= self.chunk_list.get()
			end 	= start + self.chunk_size - 1
			payload = self.get_chunck(start, end)
			with open(self.location+self._extention, 'r+b') as writer:
				writer.seek(start)
				writer.write(payload)
			self.progress(order)

	def thread_executer(self):
		threads_needed = self.threads_number
		if self.threads_number > self.divisior:
			threads_needed = self.divisior

		for th in range(threads_needed):
			t = Thread(target=self.chunk_collector)
			t.start()
			self.threads.append(t)

	def wait_until(self, var1, var2, timeout=0, period=0.25):
		wait = True
		mustend = time.time() + timeout
		while wait:
			if timeout != 0 and time.time() > mustend: wait = False
			if var1 in var2: return True
			time.sleep(period)
		return False

	def progress(self, order):
		self.progress_list.append(order)
		prec = round((len(self.progress_list)/(self.divisior))*100)
		print(f"Downloaded Section {order+1} from the file: {prec}%")
		if prec == 100:
			os.rename(self.location+self._extention, self.location)
			print("Downloaded in: {} Sec".format(round(time.time() - self.time_start, 2)))

	def download(self, auto=True):
		print(self.file)
		with open(self.location+self._extention,"wb") as f:
			f.seek(self.file.size-1)
			f.write(b'\0')

		status = self.session.get(self.file.url, 
						headers={"Range": "bytes=0-1"}, stream=True).status_code

		if (not self.file.accept_range and status != 206):
			print("Server Doesn't Support File Splitting...")
			self.split = False

		self.chunck_distreputer()

def main():
	from argparse import ArgumentParser

	parser = ArgumentParser()
	parser.add_argument("url", help="URL of the file to download")
	parser.add_argument("-n", "--name", help="Optional Custom name")
	parser.add_argument("-p", "--path", help="Change download directory path, Default: " + default_path)
	parser.add_argument("-t", "--threads", help="Maximum number of threads to use (Working only if split is avilable)")
	parser.add_argument("-s", "--no-split", action="store_true", help="Disable default file splitting behavior")

	args = parser.parse_args()

	split 	= True
	path 	= default_path
	threads = max_threads

	if args.no_split:
		split = False

	if args.path:
		path = args.path

	if args.threads:
		threads = args.threads

	try:
		Download(File(args.url, args.name), threads=threads, path=path, split=split).download()
	except KeyboardInterrupt:
		print(" Closing...")
		exit()

if __name__ == '__main__':
	main()


