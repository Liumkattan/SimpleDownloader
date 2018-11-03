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

Files are downloaded by default in `~/Videos/PyDownloader`

Also you can continue downloading interrupted downloads:
```python
from SimpleDownloader import File, Download

file = File(location="PATH_TO_INCOMPLETE_DOWNLOAD_FILE (.fuz)")

down = Download(file)

down.download()```

Or by command-line

`simpledownloader -l INCOMPLETE_DOWNLOAD_FILE.fuz`

You can also specify custom name or download path `-n NAME -p PATH`