import enum
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
            print("\nfind_group_based_on_TSSM | ii = %s" % ii)
        if ii - pointer == 1:
            group.append(ii)
            pointer = ii
            if extraordinary_signal:
                print("find_group_based_on_TSSM | pointer = %s" % pointer, "find_group_based_on_TSSM | Expanding! group = " + str(group), sep = "\n")
        else:
            if extraordinary_signal:
                print("find_group_based_on_TSSM | Deal! group = " + str(group), sep = "\n")
            groups.append(group)
            pointer = ii
            group = [pointer]
            if extraordinary_signal:
                print("find_group_based_on_TSSM | pointer = %s" % pointer, "find_group_based_on_TSSM | New group = " + str(group), sep = "\n")
                print("\nfind_group_based_on_TSSM | groups = " + str(groups), sep = "\n")
        if ii == terminator:
            groups.append(group)
            if extraordinary_signal:
                print("\nfind_group_based_on_TSSM | Terminated! groups = " + str(groups), sep = "\n")
    return groups

def find_patterning_time_interval(groups, coupled_transid_List, time_interval_List, extraordinary_signal):
    attacks = []
    evidences = []
    for group in groups:
        starter = group[0]
        length = len(group) + 1
        attacks.append(time_interval_List[starter:starter + length])
        transid_List = coupled_transid_List[starter:starter + length]
        transid_List, _ = merge_and_make_distinct_TransID_Sequences(transid_List)
        evidences.append(transid_List)
    if extraordinary_signal:
        print("\ngroups = " + str(groups), "\nattacks = " + str(attacks), "\nevidences = " + str(evidences))
    return attacks, evidences

def find_group_based_on_STD(time_interval_List, extraordinary_signal):
    groups = []
    starter = time_interval_List[0]
    group = [starter]
    terminator = len(time_interval_List) - 1
    for ii in range(1, len(time_interval_List)):
        element = time_interval_List[ii]
        if extraordinary_signal:
            print("\nfind_group_based_on_STD | element = %s" % element)

        specimen = group + [element]

        std = np.std(specimen)
        if std <= 1:
            group = specimen
            if extraordinary_signal:
                print("\nfind_group_based_on_STD | Expanding! group = " + str(group))
            if ii == terminator:
                groups.append(group)
        else:
            population = len(group)
            if population >= 2:               
                groups.append(group)
                group = [element]
            if extraordinary_signal:
                print("\nfind_group_based_on_STD | Deal! group = " + str(group))
                print("\nfind_group_based_on_STD | New group = " + str(group))
                print("\nfind_group_based_on_STD | groups = " + str(groups))
            else:
                continue
    if extraordinary_signal:
        print("\nfind_group_based_on_STD | Terminated! groups = " + str(groups))
    return groups

def find_chain_of_periods(coupled_transid_List, time_interval_List, based_on_STD, extraordinary_signal = None):
    xxx = np.abs(time_interval_List[1:] - time_interval_List[:-1])
    if extraordinary_signal:
        print("\nxxx = %s" % xxx)
    candidate_index = np.argwhere(xxx <= 1)[:, 0]
    # coupled_transid_List = 
    if len(candidate_index) == 0:
        return "", {}
    if based_on_STD:
        groups = find_group_based_on_STD(candidate_index, extraordinary_signal)
    else:
        groups = find_index_of_attack(candidate_index, extraordinary_signal)
    attacks, evidences = find_patterning_time_interval(groups, coupled_transid_List, time_interval_List, extraordinary_signal)
    periods = []
    robot_stats_info = {}
    for idx, attack in enumerate(attacks):
        # periods.append(int(np.floor(np.median(attack))))
        average_period = round(np.mean(attack), 3)
        periods.append(average_period)
        robot_stats_info[average_period] = evidences[idx]
    period_chain = ",".join([str(x) for x in periods])
    if extraordinary_signal:
        print("\nperiod_chain = %s" % period_chain, "\nrobot_stats_info = " + str(robot_stats_info))
    return period_chain, robot_stats_info

def truncate_trans_sequence(sequence_Characterized, max_length = 2000):
    sequence_length = len(sequence_Characterized)
    if sequence_length < max_length:
        return sequence_Characterized
    else:
        sequence_Characterized = sequence_Characterized[:max_length]
        sequence_Characterized = sequence_Characterized.rsplit(",", 1)
        sequence_Characterized = sequence_Characterized[0]
        return sequence_Characterized

def assign_into_PeriodRange(custID, sequence_Characterized, period_chain, robot_stats_info):
    if period_chain == "":
        # if sequence_Characterized == "":
        #     super_dangerous_tickets = 77
        # else:
        super_dangerous_tickets = sequence_Characterized.split(",")
        super_dangerous_attacks = len(super_dangerous_tickets) // 2
        # gonna_be_inserted_to_TableA_data = {"C":int(custID), "M":"", "B":"", "LI":"", "ISP":"", "DM":"", "TS":"",
        #                                     "PR0":super_dangerous_tickets, 
        #                                     "PR1":0, 
        #                                     "PR2":0, 
        #                                     "PR3":0, 
        #                                     "PR4":0, 
        #                                     "PR5":0, 
        #                                     "PR6":0, 
        #                                     "PR7":0, 
        #                                     "PR8":0, 
        #                                     "PR9":0, 
        #                                     "PR10":0}
        # gonna_be_inserted_to_TableB_data = {"C":int(custID),
        #                                     "PR0":sequence_Characterized, 
        #                                     "PR1":"", 
        #                                     "PR2":"", 
        #                                     "PR3":"", 
        #                                     "PR4":"", 
        #                                     "PR5":"", 
        #                                     "PR6":"", 
        #                                     "PR7":"", 
        #                                     "PR8":"", 
        #                                     "PR9":"", 
        #                                     "PR10":""}
        sequence_Characterized = truncate_trans_sequence(sequence_Characterized)
        gonna_be_inserted_to_DB_data = [{"C":int(custID), "R":0, "SC":super_dangerous_attacks, "TL":sequence_Characterized}]
    else:
        # gonna_be_inserted_to_TableA_data = {"C":int(custID), "M":"", "B":"", "LI":"", "ISP":"", "DM":"", "TS":"",
        #                                     "PR0":0, 
        #                                     "PR1":0, 
        #                                     "PR2":0, 
        #                                     "PR3":0, 
        #                                     "PR4":0, 
        #                                     "PR5":0, 
        #                                     "PR6":0, 
        #                                     "PR7":0, 
        #                                     "PR8":0, 
        #                                     "PR9":0, 
        #                                     "PR10":0}
        # gonna_be_inserted_to_TableB_data = {"C":int(custID),
        #                                     "PR0":"", 
        #                                     "PR1":"", 
        #                                     "PR2":"", 
        #                                     "PR3":"", 
        #                                     "PR4":"", 
        #                                     "PR5":"", 
        #                                     "PR6":"", 
        #                                     "PR7":"", 
        #                                     "PR8":"", 
        #                                     "PR9":"", 
        #                                     "PR10":""}
        # PeriodChain = cus_data["PeriodChain"] 
        # print("\n\ncustID = " + str(custID), "\nsequence_Characterized = " + sequence_Characterized, "\nperiod_chain = " + period_chain)
        # print("\nrobot_stats_info = " + str(robot_stats_info))
        gonna_be_inserted_to_DB_data = {}
        PeriodChain = period_chain.split(",")
        PeriodChain = [float(x) for x in PeriodChain]
        for element in PeriodChain:
            # print("element = " + str(element))
            order_of_range = int(element // 5) + 1
            if order_of_range > 10:
                order_of_range = 10
            if order_of_range not in gonna_be_inserted_to_DB_data:
                appended_sequence = robot_stats_info[element]
                gonna_be_inserted_to_DB_data[order_of_range] = {"C":int(custID), "R":order_of_range, "SC":1, "TL":appended_sequence}
            else:
                gonna_be_inserted_to_DB_data[order_of_range]["SC"] += 1
                appended_sequence = "," + robot_stats_info[element]
                gonna_be_inserted_to_DB_data[order_of_range]["TL"] += appended_sequence
            # print("gonna_be_inserted_to_DB_data = " + str(gonna_be_inserted_to_DB_data))
            # gonna_be_inserted_to_DB_data["PR" + str(order_of_range)] += 1
            # available_sequence = gonna_be_inserted_to_TableB_data["PR" + str(order_of_range)]
            # if available_sequence == "":
            #     appended_sequence = robot_stats_info[element]
            # else:
            #     appended_sequence = "," + robot_stats_info[element]
            # gonna_be_inserted_to_TableB_data["PR" + str(order_of_range)] += appended_sequence
        for key, value in gonna_be_inserted_to_DB_data.items():
            sequence_Characterized = value["TL"]
            sequence_Characterized = truncate_trans_sequence(sequence_Characterized)
            gonna_be_inserted_to_DB_data[key]["TL"] = sequence_Characterized
        gonna_be_inserted_to_DB_data = list(gonna_be_inserted_to_DB_data.values())
    # return gonna_be_inserted_to_TableA_data, gonna_be_inserted_to_TableB_data
    return gonna_be_inserted_to_DB_data