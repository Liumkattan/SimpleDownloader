# SimpleDownloader
Simple Python Module and Command-line tool to download files fast and easy.
it supports splitting files and download chunks simultaneously to make download faster and efficiently.
Also if internet drops in anytime it can continue downloading from where it left.

Why **SimpleDownloader** ?
+ Automated process
+ Downloading chunks simultaneously
+ Continue even after interruption
+ Flexible arguments

## Examples

Download a file:
`Download(File("URL")).download()`
Or using command-line
`simpledownloader -u URL`

Files are downloaded by default in `~/Videos/SimpleDownloader`

Also you can continue downloading interrupted downloads:
```python
from SimpleDownloader import File, Download

file = File(location="PATH_TO_INCOMPLETE_DOWNLOAD_FILE (.fuz)")

down = Download(file)

down.download()
```

Or by command-line

`simpledownloader -l INCOMPLETE_DOWNLOAD_FILE.fuz`

You can also specify custom name or download path `-n NAME -p PATH`

## Command-line --help list

```bash
usage: SimpleDownloader.py [-h] [-u URL] [-l LOCATION] [-n NAME] [-p PATH] [-r RETRY] [-s] [-t THREADS] [-v] [-V] 

optional arguments:                                                 
    -h, --help                    show this help message and exit              
    -u URL, --url URL                 URL of the file to download                 
    -l LOCATION, --location LOCATION                     location of the file on machine             
    -n NAME, --name NAME               Optional Custom name                        
    -p PATH, --path PATH                 Change download directory path, Default: $HOME/Videos/SimpleDownloader
    -r RETRY, --retry RETRY                  Set number of retrie, default is 5          
    -s, --no-split              Disable default file splitting behavior      
    -t THREADS, --threads THREADS                     Maximum number of threads to use (Working only if split is avilable)                           
    -v, --no-verbos                Disable verbosity (Do not display output), default is Displaying
    -V, --version                Display tool version and exit
```
