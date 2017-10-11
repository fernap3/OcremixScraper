import time
import re
import urllib.request
from bs4 import BeautifulSoup

def getRemixesFromPage(html):
	soup = BeautifulSoup(html, "html.parser")
	tbody = soup.find("tbody")
	
	if tbody == None:
		return None;

	rows = tbody.find_all("tr")
	
	if len(rows) == 0:
		return None

	remixes = []
	gameName = ""

	for row in rows:
		if row.has_attr("class") == False or row["class"][0] != "area-link":
			# Game title row
			gameName = row.find_all("a")[0].getText().strip()
			continue

		# Remix row
		remixRowCells = row.find_all("td")

		remixId = re.search("/remix/(OCR\d\d?\d?\d?\d?\d?)", remixRowCells[0].find("a")["href"]).group(1)
		remixTitle = remixRowCells[0].getText().replace('"', '').strip()
		datePosted = remixRowCells[3].getText().replace('"', '""').strip()
		
		remixes.append((remixId, remixTitle, gameName, datePosted))
		
	return remixes

def writeRemixesToFile(outFile, remixes):
	for remix in remixes:
		formatString = '{},"{}","{}",{}';
		print(formatString.format(remix[0], remix[1], remix[2], remix[3]), file=outFile)
	
	outFile.flush()

def scrape(outFile):
	offset = 0
	while True:
		url = "http://ocremix.org/remixes/?offset=" + str(offset)
		response = urllib.request.urlopen(url)
		data = response.read()
		html = data.decode("utf-8")

		remixes = getRemixesFromPage(html)
		
		print("Getting song info with offset " + str(offset) + "...", end="", flush=True)
		
		if remixes == None:
			print("no remixes left to get, exiting.")
			break
			
		writeRemixesToFile(outFile, remixes)
		
		print("found " + str(len(remixes)) + " remixes.  Sleeping...", flush=True)
		
		time.sleep(5)
		
		offset += 30
	
with open("remixes.csv", "w", encoding="utf-8") as outFile:
	print("id,title,game,dateposted", file=outFile)
	scrape(outFile)
	

