#-------------------------------------------------------------------------------
# Name:        Nessus5_report2csv
# Purpose:     Extract all nessus reports as CSV
#
# Author:      0x8008135
#
# Created:     26.02.2014
#-------------------------------------------------------------------------------

from xml.dom import minidom
import urllib
import urllib2
import re
import time

# http or https (to be filled)
proto=''

# ip address (to be filled)
ip=''

# port (to be filled) [int]
port=

# Output directory (to be filled)
out_dir=""

# Nessus user
login=''

# Nessus password
password=''

# dict which stores the reports (name:readableName)
reports={}


################################################################################
# Sanitize names (windows)
################################################################################
def sanitize(txt):
	ex="<>:\"/\|?*"
	for x in ex:
		if x in txt:
			txt=txt.replace(x,".")
	return txt


################################################################################
# Nessus login
################################################################################
# URL to log in Nessus
url = proto+'://'+ip+':'+str(port)+'/login'

# Credentials (to be filled)
values = {'login' : login,
          'password' : password}

# Open the url
the_page= urllib2.urlopen(urllib2.Request(url, urllib.urlencode(values))).read()

# Find the token
t=re.compile(r'.*<token>([a-f0-9]*)<\/token>.*', re.MULTILINE)
token=t.match(''.join(the_page.splitlines())).group(1)

# If token not found, exit program
if token is None:
    print "No token found ! Exiting..."
    exit()


################################################################################
# Nessus fetch reports
################################################################################
# URL to fetch reports
url = proto+'://'+ip+':'+str(port)+'/report/list'

values = {'token' : token}

# Open the url
the_page= urllib2.urlopen(urllib2.Request(url, urllib.urlencode(values))).read()

# Parse the string returned as xml
xmldoc = minidom.parseString(the_page)

# For each report store (name:readableName)
for x in range(len(xmldoc.getElementsByTagName('name'))):
    reports[xmldoc.getElementsByTagName('name').item(x).childNodes[0].data]=xmldoc.getElementsByTagName('readableName').item(x).childNodes[0].data


################################################################################
# Fetch reports in csv
################################################################################
url = proto+'://'+ip+':'+str(port)+'/file/xslt'

for rep in reports:
    values = {'token' : token,
              'report' : rep,
              'xslt' : 'csv.xsl'}
    # Open the url
    the_page= urllib2.urlopen(urllib2.Request(url, urllib.urlencode(values))).read()

    # Find the generated filename
    t=re.compile(r'.*fileName=([a-f0-9]*\.csv).*', re.MULTILINE)
    filename=t.match(''.join(the_page.splitlines())).group(1)
    # If filename not found, do nothing
    if filename is None:
        print "No filename found ! Continue..."
        exit(1)
    f=out_dir+sanitize(reports[rep])+'.csv'
    u=proto+'://'+ip+':'+str(port)+'/file/xslt/download?fileName='+filename+'&token='+token+'&step=2'

    urllib.urlretrieve(u, f)
    while '<!doctype html>' in open(f,'r').read() :
        urllib.urlretrieve(u, f)
        time.sleep(2)
