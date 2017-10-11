import time
import re
import urllib.request
from bs4 import BeautifulSoup

def getSongsFromPage(html):
	soup = BeautifulSoup(html, "html.parser")
	songRows = soup.find_all("tr", { "class": "area-link" })
	
	if len(songRows) == 0:
		return None

	songInfos = []

	for songRow in songRows:
		songRowCells = songRow.find_all("td")
		songId = int(re.search("/song/(\d\d?\d?\d?\d?\d?)", songRowCells[0].find("a")["href"]).group(1))
		songName = songRowCells[0].getText().replace('"', '').strip()
		songAliases = songRowCells[1].getText().replace('"', '""').strip()
		
		songInfos.append((songId, songName, songAliases))
		
	return songInfos

def writeSongInfosToFile(outFile, songInfos):
	for songInfo in songInfos:
		formatString = '{},"{}","{}"';
		print(formatString.format(songInfo[0], songInfo[1], songInfo[2]), file=outFile)
	
	outFile.flush()

def scrape(outFile):
	offset = 0
	while True:
		url = "http://ocremix.org/songs/?offset=" + str(offset)
		response = urllib.request.urlopen(url)
		data = response.read()
		html = data.decode("utf-8")

		songInfos = getSongsFromPage(html)
		
		print("Getting song info with offset " + str(offset) + "...", end="", flush=True)
		
		if songInfos == None:
			print("no songs left to get, exiting.")
			break
			
		writeSongInfosToFile(outFile, songInfos)
		
		print("found " + str(len(songInfos)) + " songs.  Sleeping...", flush=True)
		
		time.sleep(5)
		
		offset += 50
	
with open("songs.csv", "w", encoding="utf-8") as outFile:
	print("id,title,alias,game", file=outFile)
	scrape(outFile)
	

