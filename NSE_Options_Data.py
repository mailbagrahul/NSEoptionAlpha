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

    # from web
    # raw_data = st.get_dataframe(search_string)

    # offline data for testing
    raw_data = pd.read_csv('Option_Chain_Table.csv')
    # print(raw_data)

    raw_data_filled = raw_data.apply(lambda x: pd.to_numeric(x.astype(str).str.replace(',', ''), errors='coerce'))
    raw_data_filled.fillna(0.0, inplace=True)

    raw_data_filled['PCR_Strike'] = round(raw_data_filled['PUTS_OI'].clip_lower(1) / raw_data_filled['CALLS_OI'].clip_lower(1), 2).clip_upper(10)
    raw_data_filled['Loss_Value_Of_Calls'] = 0
    raw_data_filled['Loss_Value_Of_Puts'] = 0
    raw_data_filled['Total_Loss'] = 0

    return raw_data_filled


def fetch_and_manipulate_data(search_string):
    # from web
    Scraped_data = scraping_from_web(search_string)

    # Pass to dataframe to calculate MaxPain value
    Scrp_data_upd = NSE_Calc_Loss_Value.Calculate_Loss_Value(Scraped_data)

    Maxpain_Strike = calculate_Maxpain(Scrp_data_upd)

    PCR_Value = calculate_PCR(Scrp_data_upd)

    print("Maxpain is on:", Maxpain_Strike)
    print("PCR :", PCR_Value)

    return Scrp_data_upd
# if __name__ == '__main__':

#     search_string = "segmentLink=17&instrument=OPTIDX&symbol=BANKNIFTY&date=29NOV2018"
#     fetch_and_manipulate_data(search_string)
