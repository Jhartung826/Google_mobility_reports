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
import fitz
import json
import numpy as np

def parse_stream(stream):
    data_raw = []
    data_transformed = []
    rotparams = None
    npatches = 0
    for line in stream.splitlines():
        if line.endswith(" cm"):
            # page 146 of https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/pdf_reference_archives/PDFReference.pdf
            rotparams = list(map(float,line.split()[:-1]))
            print(rotparams)
        elif line.endswith(" l"):
            x,y = list(map(float,line.split()[:2]))
            a,b,c,d,e,f = rotparams
            xp = a*x+c*y+e
            yp = b*x+d*y+f
            data_transformed.append([xp,yp])
            data_raw.append([x,y])
        elif line.endswith(" m"):
            npatches += 1
        else:
            pass
    data_raw = np.array(data_raw)
    basex, basey = data_raw[-1]
    good = False
    if basex == 0.:
        data_raw[:,1] = basey - data_raw[:,1]
        data_raw[:,1] *= 100/60.
        data_raw = data_raw[data_raw[:,1]!=0.]
        if npatches == 1: good = True
    return dict(data=np.array(data_transformed), npatches=npatches, good=good)






class State(object):

    def __init__(self,name):
        self.name = name
        self.categories = []
        self.category_vals = []
        self.counties = []
    def add_category(self, item):
        self.categories.append(item)
    def cat_value(self, item):
        self.category_vals.append(item)
    def finalize(self, keys, values):
        self.results = dict(zip((keys),(values)))
    def add_county(self, item):
        self.counties.append(item)





class County(object):

    def __init__(self,myname, state):
        self.name = myname
        # self.state = state
        self.categories = []
        self.category_vals = []
        self.state = state
    def add_category(self, item):
        self.categories.append(item)
    def cat_value(self, item):
        self.category_vals.append(item)
    def finalize(self, keys, values):
        self.results = dict(zip(keys,values))
state = 'Alabama'
def percentage(numba):
    correct = (float(str(numba).split('%',1)[0].replace('+',''))/100)
    return correct
# def stateorcounty(action, stateaction):
#     try:
#         action
#     except AttributeError:
#         stateaction

# counter for date
c=0
# folder directories
state_dir = 'state_reports'
USA_dir = 'USA'
# list of completed dates
date_list = [report[:11] for report in os.listdir(f'{USA_dir}')]
# while True:
#     mobility_date = (dt.datetime.today()-timedelta(c)).strftime('%Y-%m-%d')
#     doc_date = (dt.datetime.today()-timedelta(c)).strftime('_%m_%d_%Y')
#     pdfus = doc_date + '_US_Mobility_Report.pdf'
#     uslink = f"https://www.gstatic.com/covid19/mobility/{mobility_date}_US_Mobility_Report_en.pdf"
#     # check to see if we completed this date
#     if doc_date in date_list:
#         completed = 'yes'
#         break
#     try:
#         urllib.request.urlretrieve(uslink, os.path.join(USA_dir, pdfus))
#         completed = 'no'
#         print(f'the latest mobility report is {mobility_date}')
#         break
#     except urllib.error.HTTPError:
#         print(f"there is no mobility report for {mobility_date}")
#         c +=1
# # download mobility reports if we haven't already
# if completed == 'no':
#     for state in states:
#         print(f'now downloading {state}')
#         state_format = state.replace(' ', '_')
#         statelink = f"https://www.gstatic.com/covid19/mobility/{mobility_date}_US_{state_format}_Mobility_Report_en.pdf"
#         # pdfstate = os.path.join(state_dir,f'{doc_date}_US_{state}_Mobility_Report.pdf')
#         pdfstate = f'{state_format}_Mobility_Report.pdf'
#         try:
#             urllib.request.urlretrieve(statelink, os.path.join(state_dir, pdfstate))
#             print(f'{mobility_date} {state} mobility report successfully downloaded')
#         except urllib.error.HTTPError:
#             print(f'failed to download {mobility_date} {state} mobility report')
# else:
#     print(f'we already have the mobility reports for {mobility_date}')
# print('all done')

doc = fitz.open(f'state_reports/Alabama_Mobility_Report.pdf')
print(doc.pageCount)
cats = ["Retail & recreation",
    "Grocery & pharmacy",
    "Parks",
    "Transit stations",
    "Workplace",
    "Residential"]
# go through each page
# if county or borough is in the item create a classify it as a county


state_list = []
county_list = []
state = 'Alabama'
# locale = None
classstate = State(state)
classstate.add_category('State')
classstate.cat_value(classstate.name)
for page in range(doc.pageCount):
    print(f'on page {page}')
    goodplots = []
    if page == 0:
        # print(doc.getPageXObjectList(page))
        # print(sorted(doc.getPageXObjectList(page), key=lambda x:int(x[1].replace("X",""))))
        xrefs = sorted(doc.getPageXObjectList(page), key=lambda x:int(x[1].replace("X","")))
        for i,xref in enumerate(xrefs):
            print(f'just the tip {doc.xrefStream(xref[0]).decode()}')
            stream = doc.xrefStream(xref[0]).decode()
            print(stream)
            info = parse_stream(stream)
            if not info["good"]: 
                continue
            else:
                goodplots.append(info)
                print(f'info right here {info}')

#     # print(len(goodplots))
#     # print(goodplots)
#     pagetext = doc.getPageText(page)
#     lines = pagetext.splitlines()
#     locale = None
#     # if page > 1:
#     for line in lines:
#         if ('County' in line and not locale is None):
#             locale.add_category('Name')
#             locale.cat_value(locale.name)
#             locale.finalize(locale.categories, locale.category_vals)
#             county_list.append(locale.results)
#             locale = County(line, state)
#         elif 'County' in line and locale is None:
#             locale = County(line, state)
#         elif any(line.startswith(c) for c in cats):
#             try:
#                 locale.add_category(line)
#             except AttributeError:
#                 classstate.add_category(line)
#         elif 'compared to baseline' in line:
#             try:
#                 locale.cat_value(percentage(line))
#             except AttributeError:
#                 continue
#         elif line == 'Not enough data for this date':
#             try:
#                 locale.cat_value('NA')
#             except AttributeError:
#                 classstate.cat_value('NA')
#             except ValueError:
#                 print(f'heres the line {line}')
#         elif ('%' in line) and (len(classstate.category_vals)<len(classstate.categories)):
#             classstate.cat_value(percentage(line))
#         # elif line == 'Baseline':
#         #     print(f'ok great {line}')
#         else:
#             continue
#     # see if we missed any county information
#     try:
#         locale.add_category('Name')
#         locale.cat_value(locale.name)
#         locale.finalize(locale.categories, locale.category_vals)
#         # attribute_list = []
#         # attribute_list.append(locale.name)
#         # attribute_list.append(locale.results)
#         county_list.append(locale.results)
#         # county_list.append(attribute_list)
#         locale = County(line, state)
#     except AttributeError:
#         print(f'no counties here')
# classstate.add_category('Counties')
# classstate.cat_value(county_list)
# classstate.finalize(classstate.categories, classstate.category_vals)
# state_list.append(classstate.results)
    # else:
    #     for line in lines:
    #         if ('County' in line and not locale is None):
    #             locale.finalize(locale.categories, locale.category_vals)
    #             attribute_list = []
    #             attribute_list.append(locale.name)
    #             attribute_list.append(locale.results)
    #             county_list.append(attribute_list)
    #             # json_list.append({locale.name: attribute_list})
    #             locale = County(line, 'Alabama')
    #         elif 'County' in line and locale is None:
    #             locale = County(line, 'Alabama')
    #         elif any(line.startswith(c) for c in cats):
    #             locale.add_category(line)
    #         elif 'compared to baseline' in line:
    #             locale.cat_value(percentage(line))
    #         elif line == 'Not enough data for this date':
    #             locale.cat_value('NA')
    #         else:
    #             continue


# with open('test.json', 'w') as outfile:
#     json.dump(state_list, outfile)

