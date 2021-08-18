import numpy as np
import pandas as pd
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
            else:
                coupled_transid_List, time_interval_List = cus_data[1]
                coupled_transid_List, time_interval_List = np.array(coupled_transid_List), np.array(time_interval_List)
                suspicious_combo = coupled_transid_List[time_interval_List < 1]
            suspicious_combo = pd.DataFrame(suspicious_combo, columns = ["matchid", "bettype", "liveindicator"])
            aa = suspicious_combo.groupby(["matchid", "bettype", "liveindicator"]).size().to_dict()
            best_combination = max(aa, key = aa.get)
            set_of_combinations = set(aa.keys())
            set_of_combinations.remove(best_combination)
            others_for_reference = ",".join(["_".join([str(x) for x in y]) for y in set_of_combinations])
            return (best_combination, others_for_reference)
        except (KeyError, ValueError):
            return None