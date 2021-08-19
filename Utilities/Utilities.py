import logging
import pandas as pd
def notify_logging(mess, isInfo = False):
    if isInfo:
        logging.info(mess)
    else:
        logging.error(mess)
    #Notifier.send_message(mess)

def merge_and_make_distinct_TransID_Sequences(coupled_transid_List):
    sequence_Characterized = "_".join(coupled_transid_List)
    sequence_Characterized = sequence_Characterized.split("_")
    sequence_Characterized = set(sequence_Characterized)
    num_suspicious_transID = len(sequence_Characterized)
    sequence_Characterized = ",".join(sequence_Characterized)
    return sequence_Characterized, num_suspicious_transID

def process_further_time_difference(coupled_transid_List, time_interval_List):
    # cus_data["4_element_TransID_Sequence"] = cus_data["2_element_TransID_Sequence"] + "_" + cus_data["2_element_TransID_Sequence"].shift(-1)
    # cus_data["second_order_Time_Difference"] = cus_data["first_order_Time_Difference"] - cus_data["first_order_Time_Difference"].shift(-1)
    # cus_data["second_order_Time_Difference"] = abs(cus_data["second_order_Time_Difference"])
    # cus_data = cus_data.dropna()
    # return cus_data
    cus_data = pd.DataFrame()
    cus_data["ID"], cus_data["TI"] = coupled_transid_List, time_interval_List
    cus_data["merged_ID"] = cus_data["ID"] + "_" + cus_data["ID"].shift(-1)
    cus_data["Difference"] = cus_data["TI"] - cus_data["TI"].shift(-1)
    cus_data["Difference"] = abs(cus_data["Difference"])
    cus_data = cus_data.dropna()
    xx, yy = cus_data["merged_ID"].values, cus_data["Difference"].values
    return xx, yy

def check_pattern(coupled_transid_List, time_interval_List):
    xx = coupled_transid_List[time_interval_List <= 1]
    yy = time_interval_List[time_interval_List <= 1]
    return xx, yy
