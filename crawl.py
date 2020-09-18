from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import urllib2
import re
from furl import furl
import csv

#this piece of code crawls the new york times website to find sunday book reviews 
#and scrapes them

#there is a csv files where the date of the review, reviewer name, author name, book name, review length and the url
#are written for each review

#add a header row to the csv file
with open("bookreviews.csv","wb") as f:
	writer = csv.writer(f)
	headers = ["Date of Review","Reviewer Name","Author Name","Book Name","Review Length(Words)","URL"]
	writer.writerow(headers)

#scrape function is the function that extracts information from a given url
#along with the data that goes to the csv file, it also extracts the review text itself and saves it to a txt file
def scrape(url):

	#hyperlink excel function to make the urls clickable in the csv
	hyperlink = "=HYPERLINK("+'"'+url+'"'+")"
	p= urllib2.build_opener(urllib2.HTTPCookieProcessor).open(url)
	html = p.read()

	#beautiful soup library is used to scrape the page
	#creating an instance of soup to search the page
	soup = BeautifulSoup(html,"lxml")

	reviewdate= soup.find("time","dateline").text.encode('utf-8').title()
	bookname = soup.findAll("p","nitf")

	#if more than 1 book, we leave them out
	if len(bookname) > 2:
		return
	elif len(bookname)==0:
		return
	else:
		booknameprint = bookname[0].text.encode('utf-8').title()

	authorname = bookname[0].next.next.next.next.encode('utf-8')

	authorname2 = soup.find("p","summary").text.encode('utf-8').title()

	#the format for author names changes quite a bit, so the next bit is to make sure all formats are accepted
	if "By " in authorname2:
		authorname2=authorname2.rsplit('By ', 1)[-1]
	elif "by " in authorname2:
		authorname2 = authorname2.rsplit('by ', 1)[-1]
	elif "By " in authorname:
		authorname2=authorname.rsplit('By ', 1)[-1]
	elif "by " in authorname:
		authorname2 = authorname.rsplit('by ', 1)[-1]
	else:
		return


	reviewername = soup.find("span","byline-author").text.encode('utf-8').title()

	wordcount=0

	#this part writes to a text file the review text and counts the words
	try:
		with open(booknameprint+' review','w') as fwrite:
			for review in soup.findAll("p","story-body-text story-content"):
				fwrite.write(review.text.encode('utf-8'))
				wordcount+=len(review.text.encode('utf-8').split())
		csvrow=[reviewdate,reviewername,authorname2,booknameprint,wordcount,hyperlink]
	except IOError:
		print "an error occured"
		return


	#this part writes the following information to the csv file: review date, reviewer name, author name, book name, wordcount
	with open("bookreviews.csv","a") as f:
		writer = csv.writer(f)
		writer.writerow(csvrow)


f = furl('http://topics.nytimes.com/svc/timestopic/v1/topic.json?limit=10&type=article%2Cblogpost&fq=%28taxonomy_nodes%3A%22Top%2FFeatures%2FBooks%2FBook+Reviews%22+OR++subject%3A%22Book+Reviews%22+OR+%28%28subject%3A%22Reviews%22+OR++type_of_material%3A%22Review%22%29+AND++subject%3A%22Books+and+Literature%22%29%29&&page=0&sort=newest')
#this part does the crawling
#it loops through the search page on the website and searches for review links
for i in range(0,76):
	f.args['page'] = i
	p = urllib2.build_opener(urllib2.HTTPCookieProcessor).open(f.url)
	html = p.read()
	html = html.replace('\\', '')

	pattern = re.compile(r'"web_url":"(.+?)"', flags=re.DOTALL)
	reviewlinks= pattern.findall(html)

	for i in range(0,10):
		print reviewlinks[i]
		reviewlink=reviewlinks[i].strip()
		#sunday book review urls have a specific format, different from normal book reviews
		#this if loop makes sure we only have the sunday book reviews
		if re.search("books/review/",reviewlink):
			scrape(reviewlink)
	
