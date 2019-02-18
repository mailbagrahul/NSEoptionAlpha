# -*- coding: utf-8 -*-
# @Author: Popeye
# @Date:   2019-02-16 13:59:32
# @Last Modified by:   Raaghul Umapathy
# @Last Modified time: 2019-02-18 07:21:22

import requests
import pandas as pd
from bs4 import BeautifulSoup

# Sample base url
# Base_url = ("https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbolCode=-10003&symbol=NIFTY&symbol=NIFTY&instrument=OPTIDX&date=-&segmentLink=17&segmentLink=17")


def scrape_data(search_string):

    base_url = "https://www.nseindia.com"
    query_prefix = "/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?"

    url = base_url + query_prefix + search_string
    # print(url)
    try:
        page = requests.get(url)
        print("Request Status code={}".format(page.status_code))
        page.content

    except:
        return "Invalid url or HTTP request failed"

    soup = BeautifulSoup(page.content, 'html.parser')

    return soup


def get_data_from_web(search_string):

    soup_data = scrape_data(search_string)
    # scrape HTML content
    table_it = soup_data.find_all(class_="opttbldata")
    table_cls_1 = soup_data.find_all(id="octable")

    col_list = []

# The code given below will pull the headers of the Option Chain table
    for mytable in table_cls_1:
        table_head = mytable.find('thead')

        try:
            rows = table_head.find_all('tr')
            for tr in rows:
                cols = tr.find_all('th')
                for th in cols:
                    er = th.text
                    ee = er.encode('utf8')
                    ee = str(ee, 'utf-8')
                    col_list.append(ee)

        except:
            print("no thead")

    col_list_fnl = [e for e in col_list if e not in ('CALLS', 'PUTS', 'Chart', '\xc2\xa0', '\xa0')]

    table_cls_2 = soup_data.find(id="octable")
    all_trs = table_cls_2.find_all('tr')
    req_row = table_cls_2.find_all('tr')

    column_names = ['CALLS_OI', 'CALLS_Chng_in_OI', 'CALLS_Volume', 'CALLS_IV', 'CALLS_LTP', 'CALLS_Net_Chng', 'CALLS_Bid_Qty', 'CALLS_Bid_Price', 'CALLS_Ask_Price', 'CALLS_Ask_Qty',
                    'Strike_Price',
                    'PUTS_Bid_Qty', 'PUTS_Bid_Price', 'PUTS_Ask_Price', 'PUTS_Ask_Qty', 'PUTS_Net_Chng', 'PUTS_LTP', 'PUTS_IV', 'PUTS_Volume',
                    'PUTS_Chng_in_OI', 'PUTS_OI']

    new_table = pd.DataFrame(index=range(0, len(req_row) - 3), columns=column_names)

    row_marker = 0

    for row_number, tr_nos in enumerate(req_row):

        # This ensures that we use only the rows with values
        if row_number <= 1 or row_number == len(req_row) - 1:
            continue

        td_columns = tr_nos.find_all('td')

        # This removes the graphs columns
        select_cols = td_columns[1:22]
        cols_horizontal = range(0, len(select_cols))

        for nu, column in enumerate(select_cols):

            utf_string = column.get_text()
            utf_string = utf_string.strip('\n\r\t": ')

            tr = utf_string.encode('utf-8')
            tr = str(tr, 'utf-8')
            tr = tr.replace(',', '')
            new_table.iloc[row_marker, [nu]] = tr

        row_marker += 1

    # Get underlying stock price
    span_list = soup_data.find_all("span")

    spot_price = span_list[0].get_text().split()[3]

    # new_table.to_csv('Option_Chain_Table.csv')
    return new_table, spot_price
