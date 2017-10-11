import time
import re
import urllib.request
from bs4 import BeautifulSoup

def getArtistInfosFromPage(html):
	soup = BeautifulSoup(html, "html.parser")
	tbody = soup.find("tbody")
	
	if tbody == None:
		return None;

	rows = tbody.find_all("tr")
	
	if len(rows) == 0:
		return None

	artistInfos = []
	gameName = ""

	for row in rows:
		if row.has_attr("class") == False or row["class"][0] != "area-link":
			# Game title row
			gameName = row.find_all("a")[0].getText().strip()
			continue

		# artistInfo row
		remixRowCells = row.find_all("td")
		
		remixId = re.search("/remix/(OCR\d\d?\d?\d?\d?\d?)", remixRowCells[0].find("a")["href"]).group(1)
		remixerLinks = remixRowCells[2].find_all("a")
		
		for link in remixerLinks:
			artistId = re.search("/artist/(\d\d?\d?\d?\d?\d?)", link["href"]).group(1)
			artistInfos.append((remixId, artistId))
		
	return artistInfos

def writeArtistInfosToFile(outFile, artistInfos):
	for artistInfo in artistInfos:
		formatString = '{},{}';
		print(formatString.format(artistInfo[0], artistInfo[1]), file=outFile)
	
	outFile.flush()

def scrape(outFile):
	offset = 0
	while True:
		url = "http://ocremix.org/remixes/?offset=" + str(offset)
		response = urllib.request.urlopen(url)
		data = response.read()
		html = data.decode("utf-8")

		artistInfos = getArtistInfosFromPage(html)
		
		print("Getting song info with offset " + str(offset) + "...", end="", flush=True)
		
		if artistInfos == None:
			print("no remix artist links left to get, exiting.")
			break
			
		writeArtistInfosToFile(outFile, artistInfos)
		
		print("found " + str(len(artistInfos)) + " remix artist links.  Sleeping...", flush=True)
		
		time.sleep(5)
		
		offset += 30
	
with open("remixartists.csv", "w", encoding="utf-8") as outFile:
	print("remixid,artistid", file=outFile)
	scrape(outFile)
	

