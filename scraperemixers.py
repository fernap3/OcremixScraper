import time
import re
import urllib.request
from bs4 import BeautifulSoup

def getRemixArtistsIdsFromPage(html):
	soup = BeautifulSoup(html, "html.parser")
	tbody = soup.find("tbody")
	
	if tbody == None:
		return None;

	rows = tbody.find_all("tr")
	
	if len(rows) == 0:
		return None

	artistIds = []

	for row in rows:
		# Remix row
		artistRowCells = row.find_all("td")
		artistNameCell = artistRowCells[1]
		artistRoleCell = artistRowCells[2]

		artistId = re.search("/artist/(\d\d?\d?\d?\d?\d?)", artistNameCell.find("a")["href"]).group(1)
		
		# Artist is not a remixer (probably a composer)
		if artistRoleCell.getText().find("ReMixer") == -1:
			continue;

		artistIds.append(artistId)
		
	return artistIds
	
def getArtistInfo(artistId):
	# artistId, artistName, realName, gender, dob
	url = "http://ocremix.org/artist/" + str(artistId)
	response = urllib.request.urlopen(url)
	data = response.read()
	html = data.decode("utf-8")
	soup = BeautifulSoup(html, "html.parser")
	
	artistHeader = soup.find("h1")
	artistName = artistHeader.contents[2].strip()
	
	try:
		realName = artistHeader.find_all("span")[1].getText().strip()
	except:
		realName = ""
	
	if soup.find("img", { "alt": "male" }) != None:
		gender = "male"
	elif soup.find("img", { "alt": "female" }) != None:
		gender = "female"
	elif soup.find("img", { "alt": "group" }) != None:
		gender = "group"
	else:
		gender = ""
		
	dob = "";
	
	for li in soup.find_all("li"):
		liText = li.getText()
		if (liText.find("Born:") != -1):
			dobMatch = re.search("\d\d\d\d-\d\d-\d\d", liText)
			
			if dobMatch != None:
				dob = dobMatch.group(0)
			break;

	artist = (artistId, artistName, realName, gender, dob)
	return artist

def writeArtistsToFile(outFile, artists):
	for artist in artists:
		formatString = '{},"{}","{}",{},{}';
		print(formatString.format(artist[0], artist[1], artist[2], artist[3], artist[4]), file=outFile, flush=True)
	
	outFile.flush()

def scrape(outFile):
	offset = 0
	while True:
		url = "http://ocremix.org/artists/?offset=" + str(offset)
		response = urllib.request.urlopen(url)
		data = response.read()
		html = data.decode("utf-8")

		artistIds = getRemixArtistsIdsFromPage(html)
		
		print("Getting artists info with offset " + str(offset) + "...", end="", flush=True)
		
		if artistIds == None:
			print("no artists left to get, exiting.")
			break
			
		print("found " + str(len(artistIds)) + " remix artists.", flush=True)
			
		for artistId in artistIds:
			artist = getArtistInfo(artistId)
			print("Got info for artist \"" + artist[1] + "\"" , flush=True)
			writeArtistsToFile(outFile, [artist])
			time.sleep(3)
		
		
		offset += 50
	
with open("remixers.csv", "w", encoding="utf-8") as outFile:
	print("id,artistname,realname,gender,dob", file=outFile, flush=True)
	scrape(outFile)
	

