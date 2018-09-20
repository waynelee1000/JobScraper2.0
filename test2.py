#base imports 
import os
import re
import csv

#BS4 parses content
from bs4 import BeautifulSoup

#allows bs4 to understand url
import requests

#faster than parsing with default html parser
import lxml

#Selenium get dynamically generated url posts
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

jobPositionList= list()
companyList = list()
hrefList = list()
gpaReqList = list()
valueList = list()
companyReviewList = list()

def getLinks():

	listURL = ("https://www.indeed.com/jobs?q=IT%20Intern&l=Philadelphia%2C%20PA&sort=date",
		"https://www.indeed.com/jobs?q=IT%20Intern&l=Philadelphia%2C%20PA&sort=date&start=10","https://www.indeed.com/jobs?q=IT%20Intern&l=Philadelphia%2C%20PA&sort=date&start=20",
		"https://www.indeed.com/jobs?q=IT%20Intern&l=Philadelphia%2C%20PA&sort=date&start=30","https://www.indeed.com/jobs?q=IT%20Intern&l=Philadelphia%2C%20PA&sort=date&start=40")

	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument('--headless')

	driver = webdriver.Chrome(chrome_options=chrome_options)

	count = 0

	for baseURL in listURL:

		driver.get(baseURL)

		divs =  driver.find_elements_by_tag_name('div')
	
		for info in divs:
			x = info.get_attribute("data-tn-component")
			if x == "organicJob":
				h2 = info.find_element_by_tag_name("h2")
				a = h2.find_element_by_tag_name("a")
				href = a.get_attribute("href")
				contentSummary(href)
				"""
				print (" ")
				count+=1
				print (count)
				print(" ")
				"""
	
	driver.quit()


def contentSummary(href):
	page  = requests.get(href)
	content =  page.content

	soup = BeautifulSoup(content, "lxml")

	jobDescript = soup.title.text


	try:
		company = soup.find(class_="company").text
	except:
		company = soup.find(class_="icl-u-lg-mr--sm icl-u-xs-mr--xs").text


	try:
		info = soup.find(class_="jobsearch-JobComponent-description icl-u-xs-mt--md").text

	except:
		info = soup.find(class_="summary").text

	jobTuple = (jobDescript,company,info)

	parseJob(jobTuple,href)


def parseJob(jobTuple,href):
	title = jobTuple[0]
	company = jobTuple[1]
	info = jobTuple[2]

#factors to add value
	gpaTuple= ("GPA Requirement is", "GPA preferred", "GPA is", "GPA:", "GPA of", "GPA","GPA: Cumulative" )

	titleTuple = ("intern","internship", "student", "co-op","college")

	skillsTuple = ("linux","java","unix","c#","selenium","docker","qa","virtualization","python")

	keyWords = ("cybersecurity","security","automation","automation","scripting","server","servers",
		"networking","network")

	value = 0

	myGPA = float (3.0)
	gpaReq = float (0)

	for titleWord in titleTuple:
		if titleWord in title.lower():
			jobRating(company)

			for gpaWord in gpaTuple:
				if gpaWord.lower() in info.lower():

					gpaNumArray = info.split(gpaWord)

					gpaBefore = gpaNumArray[0][-4:].replace(" ","")
					gpaAfter = gpaNumArray[1][:4].replace(" ","")

					try:
						gpaReq = float(gpaBefore)
					except:
						try:
							gpaReq = float(gpaAfter)
						except:
							continue


					if myGPA >= gpaReq :
						value +=1
						print(company+ " " + gpaWord + " " + str(gpaReq))
					else:
						print(company + " " + gpaWord + " "+str(gpaReq))

					break

			for skills in skillsTuple:
				if skills in info.lower():
					value+=1

			for field in keyWords:
				if field in info.lower():
					value+=1


			jobPositionList.append(title)
			companyList.append(company)
			hrefList.append(href)
			gpaReqList.append(gpaReq)
			valueList.append(value)


			break

def jobRating(company):
	reviewURL = "https://www.indeed.com/cmp/"+company
	reviewPage  = requests.get(reviewURL)
	reviewContent =  reviewPage.content

	reviewSoup = BeautifulSoup(reviewContent, "lxml")

	try:
		companyScore = reviewSoup.find(class_="cmp-header-rating-average").text
	except:
		companyScore = 0

	companyReviewList.append(companyScore)


def createCSV(jobPositionList,companyList,hrefList,gpaReqList,valueList,companyReviewList):

	pathForCSV = os.getcwd() + "\\jobData.csv"

	filedPosition = list()

	fileName = "jobData.csv"



	columnNames = ("Position","Company","URL","GPA Requirement","Value Score","Company Score")

	if os.path.exists(pathForCSV):
		with open(fileName) as file:
			reader = csv.reader(file, delimiter=',')
			for row in reader:
				filedPosition.append(row[0])
				print (row[0])

		with open(fileName,'a') as file:
			writer = csv.writer(file, delimiter=',', dialect='unix')

			for i in range (len(jobPositionList)-1):

				if not (jobPositionList[i] in filedPosition):
					dataField = (jobPositionList[i],companyList[i],hrefList[i],gpaReqList[i],valueList[i],companyReviewList[i])
					writer.writerow(dataField)


	else:
		with open(fileName,'w') as file:
				writer = csv.writer(file, delimiter=',', dialect='unix')
				writer.writerow(columnNames)

				for i in range (len(jobPositionList)-1):
					dataField = (jobPositionList[i],companyList[i],hrefList[i],gpaReqList[i],valueList[i],companyReviewList[i])
					writer.writerow(dataField)

getLinks()
createCSV(jobPositionList,companyList,hrefList,gpaReqList,valueList,companyReviewList)


exit()