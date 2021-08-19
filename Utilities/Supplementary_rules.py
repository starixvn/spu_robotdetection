import numpy as np
import pandas as pd
from Utilities.Utilities import merge_and_make_distinct_TransID_Sequences, process_further_time_difference, check_pattern
class Supplementary_rules():
    @staticmethod
    def is_Ticket_placement_so_fast(transformed_cus_data, cus_data, quickly_test_by_MBL):
        try:
            if quickly_test_by_MBL:
                # print("transformed_cus_data\n", transformed_cus_data.head())
                MBL_data = transformed_cus_data[["matchid", "bettype", "liveindicator"]].values
                time_interval_data = transformed_cus_data[transformed_cus_data.columns.difference(["matchid", "bettype", "liveindicator"])].values
                _filter = np.any(time_interval_data < 1, axis = 1)
                suspicious_combo = MBL_data[_filter]
                suspicious_combo = pd.DataFrame(suspicious_combo, columns = ["matchid", "bettype", "liveindicator"])
                aa = suspicious_combo.groupby(["matchid", "bettype", "liveindicator"]).size().to_dict()
                best_combination = max(aa, key = aa.get)
                set_of_combinations = set(aa.keys())
                set_of_combinations.remove(best_combination)
                others_for_reference = ",".join(["_".join([str(x) for x in y]) for y in set_of_combinations])
                return (best_combination, others_for_reference)
            else:
                coupled_transid_List, time_interval_List = cus_data[1]
                coupled_transid_List, time_interval_List = np.array(coupled_transid_List), np.array(time_interval_List)
                coupled_transid_List = coupled_transid_List[time_interval_List < 1]
                sequence_Characterized = merge_and_make_distinct_TransID_Sequences(coupled_transid_List)
                if sequence_Characterized == "":
                    return None
                return sequence_Characterized
        except (KeyError, ValueError):
            return None
    
    @staticmethod
    def detect_by_pattern_of_Time_Interval(cus_data, extraordinary_signal = None):
        coupled_transid_List, time_interval_List = cus_data[1]
        # cus_data = pd.DataFrame()
        # cus_data["2_element_TransID_Sequence"] = coupled_transid_List
        # cus_data["first_order_Time_Difference"] = time_interval_List
        coupled_transid_List, time_interval_List = np.array(coupled_transid_List), np.array(time_interval_List)
        xx, _ = check_pattern(coupled_transid_List, time_interval_List)
        
        # _1st_filter = cus_data[cus_data["first_order_Time_Difference"] <= 1]
        # coupled_transid_List = _1st_filter["2_element_TransID_Sequence"].to_list()
        sequence_Characterized, num_suspicious_transID = merge_and_make_distinct_TransID_Sequences(xx)
        if sequence_Characterized == "":
            # print("coupled_transid_List = %s" % coupled_transid_List, "time_interval_List = %s" % time_interval_List, "\n\n", sep = "\n")
            # for _ in range(num_iterations):
            coupled_transid_List, time_interval_List = process_further_time_difference(coupled_transid_List, time_interval_List)
            xx, _ = check_pattern(coupled_transid_List, time_interval_List)
                # if extraordinary_signal:
                #     print("coupled_transid_List = %s" % coupled_transid_List, "time_interval_List = %s" % time_interval_List, "\n\n", sep = "\n")
                # if len(xx) == 0:
                #     break
            sequence_Characterized, num_suspicious_transID = merge_and_make_distinct_TransID_Sequences(xx)
            if sequence_Characterized == "":
                return None
            else:
                return sequence_Characterized, 0, num_suspicious_transID
        else:
            return sequence_Characterized, 1, num_suspicious_transID