from states import states
import datetime as dt
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import datetime as dt
from datetime import datetime
from datetime import timedelta
import os
import urllib.request

# counter for date
c=0
# folder directories
state_dir = 'state_reports'
USA_dir = 'USA'
# list of completed dates
date_list = [report[:11] for report in os.listdir(f'{USA_dir}')]
while True:
    mobility_date = (dt.datetime.today()-timedelta(c)).strftime('%Y-%m-%d')
    doc_date = (dt.datetime.today()-timedelta(c)).strftime('_%m_%d_%Y')
    pdfus = doc_date + '_US_Mobility_Report.pdf'
    uslink = f"https://www.gstatic.com/covid19/mobility/{mobility_date}_US_Mobility_Report_en.pdf"
    # check to see if we completed this date
    if doc_date in date_list:
        completed = 'yes'
        break
    try:
        urllib.request.urlretrieve(uslink, os.path.join(USA_dir, pdfus))
        completed = 'no'
        print(f'the latest mobility report is {mobility_date}')
        break
    except urllib.error.HTTPError:
        print(f"there is no mobility report for {mobility_date}")
        c +=1
# download mobility reports if we haven't already
if completed == 'no':
    for state in states:
        print(f'now downloading {state}')
        state_format = state.replace(' ', '_')
        statelink = f"https://www.gstatic.com/covid19/mobility/{mobility_date}_US_{state_format}_Mobility_Report_en.pdf"
        # pdfstate = os.path.join(state_dir,f'{doc_date}_US_{state}_Mobility_Report.pdf')
        pdfstate = f'{state_format}_Mobility_Report.pdf'
        try:
            urllib.request.urlretrieve(statelink, os.path.join(state_dir, pdfstate))
            print(f'{mobility_date} {state} mobility report successfully downloaded')
        except urllib.error.HTTPError:
            print(f'failed to download {mobility_date} {state} mobility report')
else:
    print(f'we already have the mobility reports for {mobility_date}')
print('all done')