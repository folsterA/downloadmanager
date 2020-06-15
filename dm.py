import threading
import click
import requests

#a handler for each chunk each thread is in charge of, downloaded and written to target file
def handler(start, end, url, filename):

 #specify the starting and ending of the file
 headers = {"Range": "bytes={0}-{1}".format(start, end)}

 #use requests with the specified range in headers and put that into a variable
 r = requests.get(url, headers=headers, stream=True)

 #open the target file, and write the content of the downloaded to the target
 with open(filename, "r+b") as fp:

  fp.seek(start)
  var = fp.tell()
  fp.write(r.content)

#a main function to run on (contains clicks stuff)
@click.command(help = "It downloads the specified file with specified name")
@click.option("--number_of_threads", default = 4, help = "No. of Threads")
@click.option('--name', type = click.Path(), help = "name of the file with extention")
@click.argument("url_of_file", type = click.Path())
@click.pass_context
def download_file(ctx, url_of_file, name, number_of_threads):

 #first, we request the header, then give it a name (if the url is valid).
 r = requests.head(url_of_file)
 if name:
  file_name = name
 else:
  file_name = url_of_file.split("/")[-1]
 try:
  file_size = int(r.headers["content-length"])
 except:
  print "Invalid URL"
  return

 #next, we divide the file into equal sized parts based on the number of threads
 #and crate a file with the size ofthe content
 part = int(file_size) / number_of_threads
 with open(file_name, "wb") as fp:
  fp.write("\0" * file_size)

 #now we create the threads with the Handler function and start downloading
 for i in range(number_of_threads):
  start = part * i
  end = start + part
  t = threading.Thread(target = handler,
   kwargs = {"start": start, "end": end, "url": url_of_file, "filename": file_name})
  t.setDaemon(True)
  t.start()

 #finally, we join the threads once they've finished
 main_thread = threading.current_thread()
 for t in threading.enumerate():
  if t is main_thread:
   continue
  t.join()
 print "{0} has been downloaded".format(file_name)



#call main
if __name__ == "__main__":
 download_file(obj = {})
