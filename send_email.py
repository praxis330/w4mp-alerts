import smtplib
import unicodedata
import MimeWriter
import mimetools
import cStringIO
from datetime import date
import simplejson

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

def get_json(filename):
	with open(filename, 'r') as jobs:
		job_ads_dict = simplejson.loads(jobs.read())

	return job_ads_dict

def get_login(filename):
	with open(filename, 'r') as login_details:
		login = simplejson.loads(login_details.read())
	
	return (login[0]['email'], login[0]['password'])

def get_addresses(filename):
	emails = []
	with open(filename, 'r') as email_addresses:
		email_addresses = simplejson.loads(email_addresses.read())
		print email_addresses

	for email_address in email_addresses:
		email = email_address['email']
		emails.append(email)

	return emails


def check_job_ads(job_ads_dict):
	if job_ads_dict == []:
		return exit()

def parse_email(job_ads_dict):
	body_html = '<ul>'
	suffix_html = '</ul>'

	body_text = '-'*60

	for job_ad in job_ads_dict:
		# parse html
		html_job_ad = """
		<li style="border: solid black 1px; list-style-type: none; padding: 25px 25px; margin:0 0 10px 0">
		  <div>
		    <a href=%(url)s>%(name)s</a>
		  </div>
		  <div>
		    %(location)s
		  </div>
		  <div>
		    %(salary)s
		  </div>
		  <div>
		    %(date)s
		  </div>
		</li>
		""" % {'url': job_ad['url'], 'name': job_ad['name'], 'location': job_ad['location'], 'salary': job_ad['salary'], 'date': job_ad['date']}

		body_html += html_job_ad

		# parse text
		body_text += job_ad['name'] + '\n'
		body_text += job_ad['url'] + '\n'
		body_text += job_ad['location'] + '\n'
		body_text += job_ad['salary'] + '\n'
		body_text += job_ad['date'] + '\n'
		body_text += '-'*60 + '\n'

	# add suffix to html and encode
	body_html += suffix_html
	body_html = unicodedata.normalize('NFKD', body_html).encode('ascii', 'ignore')

	# encode text
	body_text = unicodedata.normalize('NFKD', body_text).encode('ascii', 'ignore')

	return (body_html, body_text)

def create_email(html, text, subject, fromEmail):
	out = cStringIO.StringIO()
	htmlin = cStringIO.StringIO(html)
	txtin = cStringIO.StringIO(text)

	writer = MimeWriter.MimeWriter(out)

	writer.addheader("From", fromEmail)
	writer.addheader("Subject", subject)
	writer.addheader("MIME-Version", "1.0")

	writer.startmultipartbody("alternative")
	writer.flushheaders()

	subpart = writer.nextpart()
	subpart.addheader("Content-Transfer-Encoding", "quoted-printable")
	pout = subpart.startbody("text/plain", [("charset", "utf-8")])
	mimetools.encode(txtin, pout, 'quoted-printable')

	subpart = writer.nextpart()
	subpart.addheader("Content-Transfer-Encoding", "quoted-printable")

	pout = subpart.startbody("text/html", [("charset", "utf-8")])
	mimetools.encode(htmlin, pout, 'quoted-printable')
	htmlin.close()

	writer.lastpart()
	msg = out.getvalue()
	out.close()
	return msg

if __name__=="__main__":
	import smtplib
	job_ads_dict = get_json('jobs.json')
	email, password = get_login('login.json')
	emails = get_addresses('emails.json')
	check_job_ads(job_ads_dict)
	html, text = parse_email(job_ads_dict)
	subject = 'Your w4mp alerts for %s' % TODAY
	message = create_email(html, text, subject, 'From W4MP Alerts <w4mp.alert@gmail.com>')
	server = smtplib.SMTP('smtp.gmail.com',587)
	server.ehlo()
	server.starttls()
	server.ehlo()
	server.login(email,password)
	server.set_debuglevel(1)
	for mail in emails:
		server.sendmail('w4mp.alert@gmail.com',mail,message)
	server.quit()

