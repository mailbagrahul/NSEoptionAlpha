# -*- coding: utf-8 -*-
# @Author: Popeye
# @Date:   2019-02-16 13:59:32
# @Last Modified by:   Raaghul Umapathy
# @Last Modified time: 2019-02-24 14:09:23

import pandas as pd

# import NSE_Scrape_Table_Selenium as scr_sele
import NSE_Scrape_Table as st
import NSE_Calc_Loss_Value


def calculate_Maxpain(Formatted_data):

    # print(Formatted_data)
    try:
        Maxpain = Formatted_data.loc[Formatted_data['Total_Loss'] == min(Formatted_data['Total_Loss']), 'Strike_Price'].item()
    except ValueError:
        print("Value error, conversion problem")
        return ""

    return int(Maxpain)


def calculate_PCR(Formatted_data):
    Put_Call_Ratio = round(Formatted_data['PUTS_OI'].sum() / Formatted_data['CALLS_OI'].sum(), 2)

    return Put_Call_Ratio


# To test with offline data
# raw_data = pd.read_excel("C:\\Users\\N0207022\\Desktop\\NSE_Options_BNF_10-11.xlsx")

# scrape data from web


def scraping_from_web(search_string):

    # from web with tuple
    web_raw_data = st.get_data_from_web(search_string)

    raw_data = web_raw_data[0]
    spot_price = web_raw_data[1]
    # offline data for testing
    # raw_data = pd.read_csv('Option_Chain_Table.csv')
    # print(raw_data)

    raw_data_filled = raw_data.apply(lambda x: pd.to_numeric(x.astype(str).str.replace(',', ''), errors='coerce'))
    raw_data_filled.fillna(0.0, inplace=True)

    # Get INDEXES for which OI and Volumes are zero
    dropindex = raw_data_filled[(raw_data_filled['CALLS_OI'] == 0) & (raw_data_filled['PUTS_OI'] == 0) & (raw_data_filled['CALLS_Volume'] == 0) & (raw_data_filled['PUTS_Volume'] == 0)].index

    # Delete these row indexes from dataFrame and reset the index
    raw_data_filled.drop(dropindex, inplace=True)
    raw_data_filled = raw_data_filled.reset_index(drop=True)

    raw_data_filled['PCR_Strike'] = round(raw_data_filled['PUTS_OI'].clip(lower=1) / raw_data_filled['CALLS_OI'].clip(lower=1), 2).clip(upper=10)
    raw_data_filled['Loss_Value_Of_Calls'] = 0
    raw_data_filled['Loss_Value_Of_Puts'] = 0
    raw_data_filled['Total_Loss'] = 0

    return raw_data_filled, spot_price


def fetch_and_manipulate_data(search_string):

    # from web with tuple
    Scraped_data_temp = scraping_from_web(search_string)

    Scraped_data = Scraped_data_temp[0]
    underlying_spot_price = Scraped_data_temp[1]

    # Pass to dataframe to calculate MaxPain value
    Scrp_data_upd = NSE_Calc_Loss_Value.Calculate_Loss_Value(Scraped_data)

    Maxpain_Strike = calculate_Maxpain(Scrp_data_upd)

    PCR_Value = calculate_PCR(Scrp_data_upd)

    # print("Maxpain is on:", Maxpain_Strike)
    # print("PCR :", PCR_Value)

    return Scrp_data_upd, underlying_spot_price, Maxpain_Strike, PCR_Value


# Below code is for standalone run for debug
# if __name__ == '__main__':

#     # search_string = "segmentLink=17&instrument=OPTSTK&symbol=ACC&date=28FEB2019"
#     search_string = "&symbol=INFY&date=28FEB2019"
#     fetch_and_manipulate_data(search_string)
