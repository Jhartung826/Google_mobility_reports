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
from state_list import states
from state_list import alaska_counties
from state_list import city_list
import time
# these e values will always change'
left_e = -0.46912384
mid_e =  0.4864502
right_e= 0.00866699999999998
f_top_all = [-0.34, 0.1]
f_bot_all = [-0.12, 0.33]
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

    def __init__(self,myname, state, level):
        self.name = myname
        # self.state = state
        self.categories = []
        self.category_vals = []
        self.state = state
        self.level = level
    def add_category(self, item):
        self.categories.append(item)
    def cat_value(self, item):
        self.category_vals.append(item)
    def finalize(self, keys, values):
        self.results = dict(zip(keys,values))
def percentage(numba):
    correct = (float(str(numba).split('%',1)[0].replace('+','')))
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
# date_list = [report[:11] for report in os.listdir(f'{USA_dir}')]
date_list = [report for report in os.listdir(f'{USA_dir}')]
print(date_list)
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
#         pdfstate = f'{doc_date}_{state_format}_Mobility_Report.pdf'
#         try:
#             urllib.request.urlretrieve(statelink, os.path.join(state_dir, pdfstate))
#             print(f'{mobility_date} {state} mobility report successfully downloaded')
#         except urllib.error.HTTPError:
#             print(f'failed to download {mobility_date} {state} mobility report')
# else:
#     print(f'we already have the mobility reports for {mobility_date}')
doc_date = '_06_07_2020'
print('all done')
state_list = []
for state in states:
    # doc = fitz.open(f'state_reports/{doc_date}_{state}_Mobility_Report.pdf')
    doc = fitz.open(f'state_reports/{doc_date}_{state}_Mobility_Report.pdf')
    
    print(doc.pageCount)
    cats = ["Retail & recreation",
        "Grocery & pharmacy",
        "Parks",
        "Transit stations",
        "Workplaces",
        "Residential"]
    # go through each page
    # if county or borough is in the item create a classify it as a county

    print(state)
    
    county_list = []
    # locale = None
    classstate = State(state)
    for page in range(doc.pageCount):
        # print(len(goodplots))
        # print(goodplots)
        pagetext = doc.getPageText(page)
        # print(doc.getPageXObjectList(page))
        # print(pagetext)
        lines = pagetext.splitlines()
        # with open('state_lines.txt', '+a') as chk:
        #     chk.write(f'{state} lines:\n\n {lines}')
        locale = None
        # if page > 1:
        for line in lines:
            # if state == 'Nevada':
            # if ('County' in line and not locale is None) or ('Parish' in line and not locale is None) or (line in city_list and not locale is None) or (line in alaska_counties and not locale is None) or ('City' in line and not locale is None):
            if ('County' in line or 'Parish' in line or line in city_list or line in alaska_counties or 'City' in line) and not locale is None:
                print(f'{locale.categories} and {locale.category_vals}')
                if (len(locale.category_vals)<len(locale.categories)):
                    locale.cat_value(['NA'])
                locale.finalize(locale.categories, locale.category_vals)
                locale.results['Name'] = locale.name
                locale.results['Level'] = locale.level
                county_list.append(locale.results)
                locale = County(line, state, 'bottom')
            # elif ('County' in line and locale is None) or ('Parish' in line and locale is None) or (line in city_list and locale is None) or (line in alaska_counties and locale is None) or ('City' in line and locale is None):
            elif ('County' in line or 'Parish' in line or line in city_list or line in alaska_counties or 'City' in line) and locale is None:
                locale = County(line, state, 'top')
                
            elif any(line.startswith(c) for c in cats):
                try:
                    # print(f'{locale.categories} and {locale.category_vals}')
                    if (len(locale.category_vals)<len(locale.categories)):

                        locale.cat_value(['NA'])
                        print('added NA')
                        locale.add_category(line)
                    else:
                        locale.add_category(line)

                    # print(f'{locale.name}_{line}_')
                except AttributeError:
                    classstate.add_category(line)
            elif 'compared to baseline' in line:
                try:
                    locale.cat_value([percentage(line)])
                except AttributeError:
                    continue
            elif line == 'Not enough data for this date':
                try:
                    locale.cat_value(['NA'])
                except AttributeError:
                    classstate.cat_value(['NA'])
                except ValueError:
                    print(f'heres the line {line}')
            elif ('%' in line) and (len(classstate.category_vals)<len(classstate.categories)):
                classstate.cat_value([percentage(line)])
            # elif line == 'Baseline':
            #     print(f'ok great {line}')
            else:
                continue
        # see if we missed any county information
        try:
            if (len(locale.category_vals)<len(locale.categories)):
                locale.cat_value(['NA'])
            locale.finalize(locale.categories, locale.category_vals)
            locale.results['Name'] = locale.name
            # attribute_list = []
            # attribute_list.append(locale.name)
            # attribute_list.append(locale.results)
            county_list.append(locale.results)
            # county_list.append(attribute_list)
            locale = County(line, state, 'top')
        except AttributeError:
            print(f'no counties here')
    # classstate.add_category('Counties')
    # classstate.cat_value(county_list)
    classstate.finalize(classstate.categories, classstate.category_vals)
    classstate.results['State'] = classstate.name
    classstate.results['Counties'] = county_list

    state_list.append(classstate.results)
        


data = state_list

with open(f'workplaces wtf.json', 'w') as outfile:
    json.dump(state_list, outfile)


cur_date = dt.datetime.today().strftime('%x')
# In[ ]:

all_dates = [195.2381,
    190.4762,
    185.71428,
    180.95238,
    176.19048,
    171.42857,
    166.666672,
    161.904755,
    157.142853,
    152.380951, 
    147.619049, 
    142.857147, 
    138.095245, 
    133.333328, 
    128.571426, 
    123.809525, 
    119.047623, 
    114.285713, 
    109.523811, 
    104.761902, 
    100.0, 
    95.238098, 
    90.476189, 
    85.714287, 
    80.952377, 
    76.190475, 
    71.428574, 
    66.666664, 
    61.904762, 
    57.142857, 
    52.380951, 
    47.619049, 
    42.857143, 
    38.095238, 
    33.333332, 
    28.571428, 
    23.809525, 
    19.047619, 
    14.2857141, 
    9.5238094, 
    4.7619047, 
    0.0] 
def pct_err(pred, act):
    try:
        # temp = "{:.2%}".format(abs(pred-act)/abs(act))
        temp = abs(pred-act)/abs(act)
    except ZeroDivisionError:
        temp = np.nan
    return temp

def date_converter(xaxis, yaxis, doc_date):
    global all_dates
    temp_dict = dict(zip(xaxis, yaxis))
    missing_dates = [d for d in all_dates if not d in xaxis]
    xaxis = xaxis + missing_dates
    xaxis.sort()
    new_x = []
    new_y = []
    percent_error_list = []
    switcher = {
    205: 'Actual Value',
    200.0: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(0)).strftime('%m/%d/%y'),
    195.2381: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(1)).strftime('%m/%d/%y'),
    190.4762: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(2)).strftime('%m/%d/%y'),
    185.71428: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(3)).strftime('%m/%d/%y'),
    180.95238: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(4)).strftime('%m/%d/%y'),
    176.19048: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(5)).strftime('%m/%d/%y'),
    171.42857: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(6)).strftime('%m/%d/%y'),
    166.666672: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(7)).strftime('%m/%d/%y'),
    161.904755: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(8)).strftime('%m/%d/%y'),
    157.142853: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(9)).strftime('%m/%d/%y'),
    152.380951: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(10)).strftime('%m/%d/%y'),
    147.619049: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(11)).strftime('%m/%d/%y'),
    142.857147: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(12)).strftime('%m/%d/%y'),
    138.095245: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(13)).strftime('%m/%d/%y'),
    133.333328: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(14)).strftime('%m/%d/%y'),
    128.571426: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(15)).strftime('%m/%d/%y'),
    123.809525: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(16)).strftime('%m/%d/%y'),
    119.047623: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(17)).strftime('%m/%d/%y'),
    114.285713: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(18)).strftime('%m/%d/%y'),
    109.523811: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(19)).strftime('%m/%d/%y'),
    104.761902: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(20)).strftime('%m/%d/%y'),
    100.0: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(21)).strftime('%m/%d/%y'),
    95.238098: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(22)).strftime('%m/%d/%y'),
    90.476189: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(23)).strftime('%m/%d/%y'),
    85.714287: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(24)).strftime('%m/%d/%y'),
    80.952377: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(25)).strftime('%m/%d/%y'),
    76.190475: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(26)).strftime('%m/%d/%y'),
    71.428574: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(27)).strftime('%m/%d/%y'),
    66.666664: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(28)).strftime('%m/%d/%y'),
    61.904762: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(29)).strftime('%m/%d/%y'),
    57.142857: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(30)).strftime('%m/%d/%y'),
    52.380951: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(31)).strftime('%m/%d/%y'),
    47.619049: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(32)).strftime('%m/%d/%y'),
    42.857143: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(33)).strftime('%m/%d/%y'),
    38.095238: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(34)).strftime('%m/%d/%y'),
    33.333332: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(35)).strftime('%m/%d/%y'),
    28.571428: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(36)).strftime('%m/%d/%y'),
    23.809525: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(37)).strftime('%m/%d/%y'),
    19.047619: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(38)).strftime('%m/%d/%y'),
    14.2857141: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(39)).strftime('%m/%d/%y'),
    9.5238094: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(40)).strftime('%m/%d/%y'),
    4.7619047: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(41)).strftime('%m/%d/%y'),
    0.0: (dt.datetime.strptime(doc_date,'_%m_%d_%Y')-timedelta(42)).strftime('%m/%d/%y')
        }
    for dait in xaxis:
        try:
            if dait == 205:
                percent_error_list.append(temp_dict[dait])
            elif dait == 200.0:
                percent_error_list.append(temp_dict[dait])
                new_y.append(temp_dict[dait])
                new_x.append(switcher.get(dait, 'not found'))
            else:
                new_y.append(temp_dict[dait])
                new_x.append(switcher.get(dait, 'not found'))
        except KeyError:
            new_y.append(np.nan)
            new_x.append(switcher.get(dait, 'not found'))
    try:
        pcter = pct_err(percent_error_list[0], percent_error_list[1])
    except IndexError:
        pcter = np.nan
    except TypeError:
        pcter = np.nan
    return  [[new_x, new_y],[pcter]]
def bad_graph_count(num, location):
    if (num % 2) == 0:
        num2 = num+1
    else:
        num2 = num-1
    print(f'num 1 is {num} and num 2 is {num2}')
    test = location[num]
    test2 = location[num2]
    counter = 0
    for i in test:
        if i[-1] == ' ':
            counter +=1
    for j in test2:
        if j[-1] == ' ':
            counter +=1
    return counter


# In[ ]:


bad_graph_count(10, data[0]['Counties'])


# In[ ]:





# In[ ]:

hero = 0
page = 0
def parse_stream(stream):
    data_raw = []
    data_transformed = []
    rotparams = None
    npatches = 0
    global hero
    global page
    for line in stream.splitlines():       
        # print(f" raw params are {line}")
        if line.endswith(" cm"):
            # page 146 of https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/pdf_reference_archives/PDFReference.pdf
            rotparams = list(map(float,line.split()[:-1]))
            # print(f'paramaters are {rotparams}')
        elif line.endswith(" l"):
            x,y = list(map(float,line.split()[:2]))
            a,b,c,d,e,f = rotparams
            xp = a*x+c*y+e
            yp = b*x+d*y+f
            data_transformed.append([x,yp])
            data_raw.append([x,y])
        elif line.endswith(" m"):
            npatches += 1
        else:
            pass
    data_raw = np.array(data_raw)
    # data_raw = np.array(sorted(data_raw,key=lambda x: x[0])[::-1])
    basex, basey = data_raw[-1]
    length = data_raw[:-1].shape[0]
#     print(f'basex is {basex} and {data_raw}')
    good = False
    full = length
    # if basex == 0.:
    # print(f'first {data_raw[:,1]}')
    data_raw[:,1] = basey - data_raw[:,1]
    # print(f'second {data_raw[:,1]}')
    data_raw[:,1] *= 1.6
    # data_raw[:,1] *= 100/60.
    # print(f'third and weird {data_raw[:,1]}')
    # print(f'graph {hero}')
    # print(data_raw)
    hero +=1
    data_raw = data_raw[data_raw[:,1]!=0.]
    data_raw[0]
    # print(f'final {data_raw}')
    if npatches == 1: good = True
    # print(f'length is {length} and good is {good} and {npatches}')
    return dict(data=np.array(data_raw), npatches=npatches, good=good, full=full, e = abs(round(e))+e, f = round(f-round(f),2), basex=basex, basey=basey, graphnum = hero, page=page)
# e = abs(round(e))+e

# In[ ]:



# In[ ]:
problem_states = []
e_list = []
page_list = []
weird_e_data = []
f_list = []
state_num_list = []
base_x_list = []
base_y_list = []
num_list = []
doc_page_list = []
doc_found_list = []
doc_should_list = []
doc_state_list = []
# avg_val = None
# repeat list x amount of times
def get_bases():
    e_list.append(goodplots[p]['e'])
    # b_list.append(goodplots[p]['left_a'])
    # c_list.append(goodplots[p]['mid_a'])
    # d_list.append(goodplots[p]['right_a'])
    f_list.append(goodplots[p]['f'])
    base_x_list.append(goodplots[p]['basex'])
    base_y_list.append(goodplots[p]['basey'])
    num_list.append(goodplots[p]['graphnum'])
    page_list.append(goodplots[p]['page'])
    # average_l_list.append(average_l)
    # average_m_list.append(average_m)
    # average_r_list.append(average_r)

s = 0
for state in states:
    f_vals = []
    xaxisdate = dt.datetime.strptime(doc_date,'_%m_%d_%Y').strftime('%m/%d/%y')
    p=0
    pages = 2
    doc = fitz.open(f'state_reports/{doc_date}_{state}_Mobility_Report.pdf')
    goodplots = []
    page_plots = []
    page_plotsall = []
    page_average = []
    pagelist = []
    pagenum = 0
    grahnum = 0
    hero = 0
    averages = []
    for page in range(doc.pageCount):
        pagelist.append(pagenum)
        pagenum +=1
        try:
            page_plotsall.append(len(goodplots))
        except NameError:
            print('nothing here')
        xrefs = sorted(doc.getPageXObjectList(page), key=lambda x:int(x[1].replace("X","")))
        local_all = []
        for i,xref in enumerate(xrefs):
            grahnum +=1
    #         print(f'just the tip {doc.xrefStream(xref[0]).decode()}')
            stream = doc.xrefStream(xref[0]).decode()
            # print(stream)
            # print(stream)
            # print(doc.xrefStream(xref[0]).decode())
            info = parse_stream(stream)
            print(f"f is {info['f']}")
            if info['f'] !='nan':
                local_all.append(info['f'])
                graph_len = len(local_all)
            goodplots.append(info)
        # 
        # local_all = list(set(local_all))
        avg_val = np.mean(np.array(list(set(local_all))))
        page_average.append(avg_val)
        print(f'page_average {len(page_average)}')

    gn = 0

    graphcounter = dict(zip(pagelist, page_plotsall))
    # page_average_dict = dict(zip(page_list, page_average))
    print(f'page average finder {page_average}')
    # print(f'{state}')
    try:
        # print(f'retail for {state} is on page {page}')
        Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] + data[s]['Retail & recreation']
        X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
        data[s]['Retail & recreation'] = date_converter(X,Y, doc_date)[0]
        data[s]['Retail & recreation Percent Error'] = date_converter(X,Y, doc_date)[1]
        print(f' retail e is {goodplots[p]["e"]}')
        # with open('textversion.txt', 'a+') as outfile:
        #     outfile.write(f"{data[s]['Retail & recreation']}\n\n our parameter e: {goodplots[p]['e']} and parameter f: {goodplots[p]['f']}\n\n\n\n\n\n")
        # with open('date_comparison.json', 'w') as outfile:
        #     json.dump(data, outfile)
        p +=1
    except KeyError:
        data[s]['Retail & recreation'] = data[s].pop('Retail & recreation ')
    try:
        Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] +  data[s]['Grocery & pharmacy']
        X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
        data[s]['Grocery & pharmacy'] = date_converter(X,Y, doc_date)[0]
        data[s]['Grocery & pharmacy Percent Error'] = date_converter(X,Y, doc_date)[1]
        p +=1
        print(f' groc e is {goodplots[p]["e"]}')
        # with open('textversiongroc.txt', 'a+') as outfile:
        #     outfile.write(f"{data[s]['Grocery & pharmacy']}\n\n our parameter e: {goodplots[p]['e']} and parameter f: {goodplots[p]['f']}\n\n\n\n\n\n")
    except KeyError:
        print(f'bingo for {state}')
        data[s]['Grocery & pharmacy'] = data[s].pop('Grocery & pharmacy ')
    try:
        Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] +  data[s]['Parks']
        X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
        data[s]['Parks'] = date_converter(X,Y, doc_date)[0]
        data[s]['Parks Percent Error'] = date_converter(X,Y, doc_date)[1]
        print(f'parks e is {goodplots[p]["f"]}')
        p +=1
    except KeyError:
        print(f'bingo for {state}')
        data[s]['Parks'] = data[s].pop('Parks ')
    try:
        Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] +  data[s]['Transit stations']
        X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
        data[s]['Transit stations'] = date_converter(X,Y, doc_date)[0]
        data[s]['Transit stations Percent Error'] = date_converter(X,Y, doc_date)[1]
        print(f'transit e is {goodplots[p]["e"]}')
        p +=1
    except KeyError:
        print(f'bingo for {state}')
        data[s]['Transit stations'] = data[s].pop('Transit stations ')
    try:
        Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] +  data[s]['Workplaces']
        X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
        data[s]['Workplaces'] = date_converter(X,Y, doc_date)[0]
        data[s]['Workplaces Percent Error'] = date_converter(X,Y, doc_date)[1]
        print(f'work e is {goodplots[p]["e"]}')
        p +=1
    except KeyError:
        print(f'bingo for {state}')
        data[s]['Workplaces'] = data[s].pop('Workplaces ')
    try:
        # print(f'residential for {state} is on page {page}')
        Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] +  data[s]['Residential']
        X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
        data[s]['Residential'] = date_converter(X,Y, doc_date)[0]
        data[s]['Residential Percent Error'] = date_converter(X,Y, doc_date)[1]
        print(f'res e is {goodplots[p]["e"]}')
        p +=1
    except KeyError:
        print(f'bingo for {state}')
        data[s]['Residential'] = data[s].pop('Residential ')
    for c in range(len(data[s]['Counties'])):
        if (c % 2) == 0:
            # if state in problem_states:
            f_top = [f_top_all[0]]
            f_bot = [f_bot_all[0], -0.11]
            print(f'for {state} on page {pages} and went through {p} graphs but should have {graphcounter[pages]}')
            doc_page_list.append(pages)
            doc_found_list.append(p)
            doc_should_list.append(graphcounter[pages])
            doc_state_list.append(state)
            pages +=1
        else:
            f_top = [f_top_all[1], 0.11]
            f_bot = [f_bot_all[1], 0.32]
        try:
            print(s)
            if data[s]['Counties'][c]['Retail & recreation'] != 'NA':
            # print(f"{data[s]['Counties'][c]['Name']} on page {pages}")
            # if abs(abs(goodplots[p]["e"]) - abs(left_e)) < .0001 and (goodplots[p]["f"] > 0 or goodplots[p]["f"]  == -0.17 or goodplots[p]["f"]  == -0.16):
                if abs(abs(goodplots[p]["e"]) - abs(left_e)) < .0001 and goodplots[p]["f"] in f_top:
                    Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] + data[s]['Counties'][c]['Retail & recreation'] 
                    X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
                    data[s]['Counties'][c]['Retail & recreation'] = date_converter(X,Y, doc_date)[0]
                    data[s]['Counties'][c]['Retail & recreation Percent Error'] = date_converter(X,Y, doc_date)[1]
                    # data[s]['Counties'][c]['Retail Graphs'] = [goodplots[p]["e"], goodplots[p]["f"], goodplots[p]["basex"], goodplots[p]["basey"]]
                    
                    p +=1
                else:
                    print(f"its a no go for {data[s]['Counties'][c]['Name']}  at {goodplots[p]['e']} {goodplots[p]['f']} retail")
        except KeyError:
            data[s]['Counties'][c]['Retail & recreation'] = data[s]['Counties'][c].pop('Retail & recreation ')
            if data[s]['Counties'][c]['Retail & recreation'][0] != 'NA' and abs(abs(goodplots[p]["e"]) - abs(left_e)) < .0001 and (goodplots[p]["f"] > 0 or goodplots[p]["f"]  == -0.17 or goodplots[p]["f"]  == -0.16):
                Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] + data[s]['Counties'][c]['Retail & recreation']
                X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
                data[s]['Counties'][c]['Retail & recreation'] = date_converter(X,Y, doc_date)[0]
                data[s]['Counties'][c]['Retail & recreation Percent Error'] = date_converter(X,Y, doc_date)[1]
                p +=1
            else:
                print(f"its a no go for {data[s]['Counties'][c]['Name']}  at {goodplots[p]['f']}  retail")
            # elif state in problem_states:
            #     print(f"{data[s]['Counties'][c]['Name']} state {state} is not good and e is {goodplots[p]['e']} and basex is {goodplots[p]['basex']} rtail")
            #     print(goodplots[p]['data'])
        try:
            if data[s]['Counties'][c]['Grocery & pharmacy'] != 'NA':
                # if abs(abs(goodplots[p]["e"]) - abs(mid_e)) < .0001 and (goodplots[p]["f"] > 0 or goodplots[p]["f"]  == -0.17 or goodplots[p]["f"]  == -0.16):
                if abs(abs(goodplots[p]["e"]) - abs(mid_e)) < .0001 and goodplots[p]["f"] in f_top:
                    Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] + data[s]['Counties'][c]['Grocery & pharmacy']
                    X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
                    data[s]['Counties'][c]['Grocery & pharmacy'] = date_converter(X,Y, doc_date)[0]
                    data[s]['Counties'][c]['Grocery & pharmacy Percent Error'] = date_converter(X,Y, doc_date)[1]

                    # if state in problem_states and c >59:
                    #     print()
                    p +=1
                else:
                    print(f"its a no go for {data[s]['Counties'][c]['Name']}  at {goodplots[p]['e']} {goodplots[p]['f']}  grocery")
        except KeyError:
            data[s]['Counties'][c]['Grocery & pharmacy'] = data[s]['Counties'][c].pop('Grocery & pharmacy ')
            if data[s]['Counties'][c]['Grocery & pharmacy'][0] != 'NA' and abs(abs(goodplots[p]["e"]) - abs(mid_e)) < .0001 and (goodplots[p]["f"] > 0 or goodplots[p]["f"]  == -0.17 or goodplots[p]["f"]  == -0.16):
                Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] + data[s]['Counties'][c]['Grocery & pharmacy']
                X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
                data[s]['Counties'][c]['Grocery & pharmacy'] = date_converter(X,Y, doc_date)[0]
                data[s]['Counties'][c]['Grocery & pharmacy Percent Error'] = date_converter(X,Y, doc_date)[1]
                # data[s]['Counties'][c]['Grocery & pharmacy Graphs'] = [goodplots[p]["e"], goodplots[p]["f"], goodplots[p]["basex"], goodplots[p]["basey"]]

                p +=1
            else:
                print(f"its a no go for {data[s]['Counties'][c]['Name']}  at {goodplots[p]['f']}  grocery")
            # elif state in problem_states:
            #     print(f"{data[s]['Counties'][c]['Name']} state {state} is not good and e is {goodplots[p]['e']} and basex is {goodplots[p]['basex']} groc")
            #     print(goodplots[p]['data'])
        try:
            if data[s]['Counties'][c]['Parks'] != 'NA': 
                # if abs(abs(goodplots[p]["e"]) - abs(right_e)) < .0001 and (goodplots[p]["f"] > 0 or goodplots[p]["f"]  == -0.17 or goodplots[p]["f"]  == -0.16):
                if abs(abs(goodplots[p]["e"]) - abs(right_e)) < .0001 and goodplots[p]["f"] in f_top:
                    Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] + data[s]['Counties'][c]['Parks']
                    X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
                    data[s]['Counties'][c]['Parks'] = date_converter(X,Y, doc_date)[0]
                    data[s]['Counties'][c]['Parks Percent Error'] = date_converter(X,Y, doc_date)[1]
                    # data[s]['Counties'][c]['Parks Graphs'] = [goodplots[p]["e"], goodplots[p]["f"], goodplots[p]["basex"], goodplots[p]["basey"]]

                    p +=1
                else:
                    print(f"its a no go for {data[s]['Counties'][c]['Name']}  at {goodplots[p]['e']} {goodplots[p]['f']}  Parks")

        except KeyError:
            data[s]['Counties'][c]['Parks'] = data[s]['Counties'][c].pop('Parks ')
            if data[s]['Counties'][c]['Parks'][0] != 'NA' and abs(abs(goodplots[p]["e"]) - abs(right_e)) < .0001 and (goodplots[p]["f"] > 0 or goodplots[p]["f"]  == -0.17 or goodplots[p]["f"]  == -0.16):
                Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] + data[s]['Counties'][c]['Parks']
                X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
                data[s]['Counties'][c]['Parks'] = date_converter(X,Y, doc_date)[0]
                data[s]['Counties'][c]['Parks Percent Error'] = date_converter(X,Y, doc_date)[1]
                p +=1
            else:
                print(f"its a no go for {data[s]['Counties'][c]['Name']}  at {goodplots[p]['f']}  parks")
            # elif state in problem_states:
            #     print(f"{data[s]['Counties'][c]['Name']} state {state} is not good and e is {goodplots[p]['e']} and basex is {goodplots[p]['basex']} parks")
            #     print(goodplots[p]['data'])
        try:
            if data[s]['Counties'][c]['Transit stations'] != 'NA':
            # if abs(abs(goodplots[p]["e"]) - abs(left_e)) < .0001 and (goodplots[p]["f"] < 0 or goodplots[p]["f"]  == 0.29 or goodplots[p]["f"]  == 0.30):
                if abs(abs(goodplots[p]["e"]) - abs(left_e)) < .0001 and goodplots[p]["f"] in f_bot:
                    Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] + data[s]['Counties'][c]['Transit stations']
                    X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
                    data[s]['Counties'][c]['Transit stations'] = date_converter(X,Y, doc_date)[0]
                    data[s]['Counties'][c]['Transit stations Percent Error'] = date_converter(X,Y, doc_date)[1]
                    # data[s]['Counties'][c]['Transit Graphs'] = [goodplots[p]["e"], goodplots[p]["f"], goodplots[p]["basex"], goodplots[p]["basey"]]

                    # print(f"transit stations for {data[s]['Counties'][c]['Name']} is legit with base y of {goodplots[p]['basey']}")
                    p +=1
                else:
                    print(f"its a no go for {data[s]['Counties'][c]['Name']}  at {goodplots[p]['e']} {goodplots[p]['f']}  transit")
        except KeyError:
            # data[s]['Counties'][c]['Transit stations'] = data[s]['Counties'][c].pop('Transit stations ')
            if data[s]['Counties'][c]['Transit stations'][0] != 'NA' and abs(abs(goodplots[p]["e"]) - abs(left_e)) < .0001 and (goodplots[p]["f"] < 0 or goodplots[p]["f"]  == 0.29 or goodplots[p]["f"]  == 0.30):
                Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] + data[s]['Counties'][c]['Transit stations']
                X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
                data[s]['Counties'][c]['Transit stations'] = date_converter(X,Y, doc_date)[0]
                data[s]['Counties'][c]['Transit stations Percent Error'] = date_converter(X,Y, doc_date)[1]
                p +=1
            else:
                print(f"its a no go for {data[s]['Counties'][c]['Name']}  at {goodplots[p-1]['f']}  transit")
            # elif state in problem_states:
            #     print(f"{data[s]['Counties'][c]['Name']} state {state} is not good and e is {goodplots[p]['e']} and basex is {goodplots[p]['basex']} transit")
            #     print(goodplots[p]['data'])
        try:
            # print(f'{state} at s {s} c {c}')
            if data[s]['Counties'][c]['Workplaces'][0] != 'NA':
                # if abs(abs(goodplots[p]["e"]) - abs(mid_e)) < .0001 and (goodplots[p]["f"] < 0 or goodplots[p]["f"]  == 0.29 or goodplots[p]["f"]  == 0.30):
                if abs(abs(goodplots[p]["e"]) - abs(mid_e)) < .0001 and goodplots[p]["f"] in f_bot:
                    Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] + data[s]['Counties'][c]['Workplaces']
                    X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
                    data[s]['Counties'][c]['Workplaces'] = date_converter(X,Y, doc_date)[0]
                    data[s]['Counties'][c]['Workplaces Percent Error'] = date_converter(X,Y, doc_date)[1]
                    p +=1
                else:
                    print(f"its a no go for {data[s]['Counties'][c]['Name']}  at {goodplots[p]['e']} {goodplots[p]['f']}  workplace")
        except KeyError:
            # print(p)
            if data[s]['Counties'][c]['Workplaces'][0] != 'NA' and abs(abs(goodplots[p]["e"]) - abs(mid_e)) < .0001 and (goodplots[p]["f"] < 0 or goodplots[p]["f"]  == 0.29 or goodplots[p]["f"]  == 0.30):
                Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] + data[s]['Counties'][c]['Workplaces']
                X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
                data[s]['Counties'][c]['Workplaces'] = date_converter(X,Y, doc_date)[0]
                data[s]['Counties'][c]['Workplaces Percent Error'] = date_converter(X,Y, doc_date)[1]
                p +=1
            else:
                print(f"its a no go for {data[s]['Counties'][c]['Name']}  at {goodplots[p]['f']}  workplace")
        try:
            # print(f'{s} and c {c}')
            print(f"our last item is {data[s]['Counties'][c]['Residential']}")
            # if abs(abs(goodplots[p]["e"]) - abs(right_e)) < .0001 and (goodplots[p]["f"] < 0 or goodplots[p]["f"]  == 0.29 or goodplots[p]["f"]  == 0.30):
            if data[s]['Counties'][c]['Residential'][0] != 'NA':
                if abs(abs(goodplots[p]["e"]) - abs(right_e)) < .0001 and goodplots[p]["f"] in f_bot:
                    Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] + data[s]['Counties'][c]['Residential']
                    X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
                    data[s]['Counties'][c]['Residential'] = date_converter(X,Y, doc_date)[0]
                    data[s]['Counties'][c]['Residential Percent Error'] = date_converter(X,Y, doc_date)[1]
                    p +=1
                else:
                    print(f"its a no go for {data[s]['Counties'][c]['Name']}  at {goodplots[p]['e']} {goodplots[p]['f']}  residential")
        except KeyError:
            # data[s]['Counties'][c]['Residential'] = data[s]['Counties'][c].pop('Residential ')
            if data[s]['Counties'][c]['Residential'][0] != 'NA' and abs(abs(goodplots[p]["e"]) - abs(right_e)) < .0001 and (goodplots[p]["f"] < 0 or goodplots[p]["f"]  == 0.29 or goodplots[p]["f"]  == 0.30):
                Y = goodplots[p]['data'].transpose()[1].tolist()[::-1] + data[s]['Counties'][c]['Residential']
                X = goodplots[p]['data'].transpose()[0].tolist()[::-1] + [205]
                data[s]['Counties'][c]['Residential'] = date_converter(X,Y, doc_date)[0]
                data[s]['Counties'][c]['Residential Percent Error'] = date_converter(X,Y, doc_date)[1]
                p +=1
            else:
                print(f"its a no go for {data[s]['Counties'][c]['Name']}  at {goodplots[p-1]['f']}  res")
            # elif state in problem_states:
            #     print(f"{data[s]['Counties'][c]['Name']} state {state} is not good and e is {goodplots[p]['e']} and basex is {goodplots[p]['basex']} res")
            #     print(goodplots[p]['data'])
    s+=1
    try:
        # goodplots[p]['data'].transpose()[1].tolist()
        goodplots[p]
        if state == 'Virginia':
            print(goodplots[p])
        with open('newcheck.txt', '+a') as chk:
            chk.write(f'{state} is not good so {p} needed graphs but there are {graphcounter[pages]} found graphs  \n')
    except IndexError:
        with open('newcheck.txt', '+a') as chk:
            chk.write(f'{state} looks GOOD!!!!!!!!! these should be one off {p} and {graphcounter[pages]}\n')

# In[ ]:

# In[ ]:

with open(f'{doc_date}_Mobility.json', 'w') as outfile:
    json.dump(data, outfile)

