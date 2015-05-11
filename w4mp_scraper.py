import requests
import bs4
import re
from datetime import date
import unicodedata
import json

BASE_URL = 'http://www.w4mpjobs.org/'

MONTHS =   {1: 'January',
			2: 'February', 
			3: 'March', 
			4: 'April', 
			5: 'May', 
			6: 'June', 
			7: 'July', 
			8: 'August', 
			9: 'September', 
			10: 'October', 
			11: 'November', 
			12: 'December'
	}

TODAY = str(date.today().day) + ' ' + MONTHS[date.today().month]

def get_job_ads(url):
	page = requests.get(url)
	page = bs4.BeautifulSoup(page.text)
	page_results = page.select('ul.searchresults')[0]
	job_ads = page_results.find_all('li')
	return job_ads

def parse(job_ads):
	job_ads_list = []

	for job_ad in job_ads:
		job_date = job_ad.select('div[id="dates"]')[0].get_text()
		if re.search(TODAY, job_date):
			job = {}

			name = job_ad.select('div[id=jobid]')[0].get_text()
			job['name'] = name[7:].strip()

			job['location'] = job_ad.select('div[id="location"]')[0].get_text()
			job['salary'] = job_ad.select('div[id="salary"]')[0].get_text()
			job['date'] = job_ad.select('div[id="dates"]')[0].get_text()
			job['url'] = BASE_URL + job_ad.select('div[id="moredetailslink"] a')[0].get('href')
			
			job_ads_list.append(job)
		else:
			break
	return job_ads_list

def to_json(job_ads_list):
	with open('jobs.json', 'w') as jobs_file:
		return json.dump(job_ads_list, jobs_file)

def retry_if_connection_error(retries=0):
	counter = 0
	while counter <= retries:
		try:
			return get_job_ads(BASE_URL + 'SearchJobs.aspx?search=nmwandabove')
			break
		except requests.exceptions.ConnectionError:
			counter += 1

if __name__ == '__main__':
	job_ads = retry_if_connection_error(retries=5)
	job_ads_list = parse(job_ads)
	to_json(job_ads_list)


