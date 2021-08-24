import logging
import pandas as pd
import numpy as np
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

def substract_2_sucessive_elements_and_merge_transID(coupled_transid_List, time_interval_List):
    cus_data = pd.DataFrame()
    cus_data["ID"], cus_data["TI"] = coupled_transid_List, time_interval_List
    cus_data["merged_ID"] = cus_data["ID"] + "_" + cus_data["ID"].shift(-1)
    cus_data["Difference"] = cus_data["TI"] - cus_data["TI"].shift(-1)
    cus_data["Difference"] = abs(cus_data["Difference"])
    cus_data = cus_data.dropna()
    xx, yy = cus_data["merged_ID"].values, cus_data["Difference"].values
    return xx, yy

def add_2_sucessive_elements_and_merge_transID(coupled_transid_List, time_interval_List):
    cus_data = pd.DataFrame()
    cus_data["ID"], cus_data["TI"] = coupled_transid_List, time_interval_List
    cus_data["merged_ID"] = cus_data["ID"] + "_" + cus_data["ID"].shift(-1)
    cus_data["Summation"] = cus_data["TI"] + cus_data["TI"].shift(-1)
    cus_data["Summation"] = abs(cus_data["Summation"])
    cus_data = cus_data.dropna()
    xx, yy = cus_data["merged_ID"].values, cus_data["Summation"].values
    return xx, yy

def check_pattern(coupled_transid_List, time_interval_List, is_third_order = 0):
    if is_third_order:
        xx = coupled_transid_List[time_interval_List <= 2]
        yy = time_interval_List[time_interval_List <= 2]
    else:
        xx = coupled_transid_List[time_interval_List <= 1]
        yy = time_interval_List[time_interval_List <= 1]
    return xx, yy

def find_index_of_attack(candidate_index, extraordinary_signal):
    groups = []
    # group = [candidate_index[0]]
    pointer = candidate_index[0]
    group = [pointer]
    terminator = candidate_index[-1]
    for ii in candidate_index[1:]:
        if extraordinary_signal:
            print("\nii = %s" % ii)
        if ii - pointer == 1:
            group.append(ii)
            pointer = ii
            if extraordinary_signal:
                print("pointer = %s" % pointer, "Expanding! group = " + str(group), sep = "\n")
        else:
            if extraordinary_signal:
                print("Deal! group = " + str(group), sep = "\n")
            groups.append(group)
            pointer = ii
            group = [pointer]
            if extraordinary_signal:
                print("pointer = %s" % pointer, "New group = " + str(group), sep = "\n")
                print("\ngroups = " + str(groups), sep = "\n")
        if ii == terminator:
            groups.append(group)
            if extraordinary_signal:
                print("\nTerminated! groups = " + str(groups), sep = "\n")
    return groups

def find_patterning_time_interval(groups, time_interval_List):
    attacks = []
    for group in groups:
        starter = group[0]
        length = len(group) + 1
        attacks.append(time_interval_List[starter:starter + length])
    return attacks

def find_chain_of_periods(time_interval_List, extraordinary_signal = None):
    xxx = np.abs(time_interval_List[1:] - time_interval_List[:-1])
    if extraordinary_signal:
        print("\nxxx = %s" % xxx)
    candidate_index = np.argwhere(xxx <= 1)[:, 0]
    if len(candidate_index) == 0:
        return ""
    groups = find_index_of_attack(candidate_index, extraordinary_signal)
    attacks = find_patterning_time_interval(groups, time_interval_List)
    periods = []
    for attack in attacks:
        # periods.append(int(np.floor(np.median(attack))))
        periods.append(round(np.mean(attack), 3))
    period_chain = ",".join([str(x) for x in periods])
    if extraordinary_signal:
        print("\nperiod_chain = %s" % period_chain)
    return period_chain
