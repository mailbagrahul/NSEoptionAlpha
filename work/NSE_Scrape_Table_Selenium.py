from io import StringIO
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import pandas as pd

"""
reference websearcher browser_driver.py
https://github.com/beepscore/websearcher
"""


def get_octable_text(search_string):
    """
    Use browser to request info
    wait for javascript to run and return html for id
    return empty string if timeout or error
    """
    # browser = webdriver.Firefox()
    browser = webdriver.Chrome()

    base_url = "https://www.nseindia.com"
    query_prefix = "/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?"

    url = base_url + query_prefix + search_string
    browser.get(url)

    try:
        # http://stackoverflow.com/questions/37422832/waiting-for-a-page-to-load-in-selenium-firefox-w-python?lq=1
        # http://stackoverflow.com/questions/5868439/wait-for-page-load-in-selenium
        id_octable = "octable"
        WebDriverWait(browser, 6).until(lambda d: d.find_element_by_id(id_octable).is_displayed())
        octable = browser.find_element_by_id(id_octable)
        return octable.text

    except TimeoutException:
        print("TimeoutException, returning empty string")
        return ""

    except AttributeError:
        # http://stackoverflow.com/questions/9823936/python-how-do-i-know-what-type-of-exception-occured#9824050
        print("AttributeError, returning empty string")
        return ""

    finally:
        browser.quit()


def get_dataframe(search_string):
    """
    :param search_string:
    :return: dataframe
    """

    # avoid duplicate column names
    # column_names = ['c_oi', 'c_chng_in_oi', 'c_volume', 'c_iv', 'c_ltp',
    #                 'c_net_chng', 'c_bid_qty', 'c_bid_price', 'c_ask_price', 'c_ask_qty',
    #                 'strike price',
    #                 'p_bid_qty', 'p_bid_price', 'p_ask_price', 'p_ask_qty',
    #                 'p_net chng', 'p_ltp', 'p_iv', 'p_volume', 'p_chng_in_oi', 'p_oi']

    column_names = ['CALLS_OI', 'CALLS_Chng_in_OI', 'CALLS_Volume', 'CALLS_IV', 'CALLS_LTP', 'CALLS_Net_Chng', 'CALLS_Bid_Qty', 'CALLS_Bid_Price', 'CALLS_Ask_Price', 'CALLS_Ask_Qty',
                    'Strike_Price',
                    'PUTS_Bid_Qty', 'PUTS_Bid_Price', 'PUTS_Ask_Price', 'PUTS_Ask_Qty', 'PUTS_Net_Chng', 'PUTS_LTP', 'PUTS_IV', 'PUTS_Volume',
                    'PUTS_Chng_in_OI', 'PUTS_OI']
    # read from local data file
    # this can be handy during development
    # df = pd.read_csv('./data/octable.txt', sep=' ', names=column_names, skiprows=10)

    # read from web
    octable_text = get_octable_text(search_string)
    # https://stackoverflow.com/questions/20696479/pandas-read-csv-from-string-or-package-data
    df = pd.read_csv(StringIO(octable_text), dtype=object, sep=' ', names=column_names, skiprows=10)

    return df


# search_string = "segmentLink=17&instrument=OPTIDX&symbol=BANKNIFTY&date=25OCT2018"
# dfd = get_dataframe(search_string)
# print(dfd)
