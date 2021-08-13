import numpy as np
import datetime
import pandas as pd

class Prepare_Data_for_each_user():
    def __init__(self, custid):
        self.custid = custid
        
    def convert_datetime_to_seconds(self, list_of_strtime, strtime_format):
        time_interval_arr = []
        for ii in range(1, len(list_of_strtime)):
            xx = datetime.datetime.strptime(list_of_strtime[ii], strtime_format)
            x = datetime.datetime.strptime(list_of_strtime[ii - 1], strtime_format)
            time_interval_arr.append((xx - x).total_seconds())
        return time_interval_arr
    
    def build_dictionary_pre_TIM(self, strtime_format, data, is_detected_by_MBL):
        if is_detected_by_MBL:
            cus_data = data[data.custid == self.custid][["custid", "transdate", "matchid", 
                                                        "bettype", "liveindicator"]]
            cus_data = cus_data.groupby(["matchid", "bettype", "liveindicator"])["transdate"] \
                    .agg(lambda z: sorted(list(z)))
            cus_data = cus_data.apply(lambda z: self.convert_datetime_to_seconds(z, strtime_format))
        else:
            cus_data = data[data.custid == self.custid][["custid", "transdate", "transid"]]
            cus_data = cus_data.sort_values("transdate")
            cus_data["coupled_transid"] = cus_data["transid"].map(str) + "_" + cus_data["transid"].map(str).shift(-1)
            cus_data["datetime_object"] = cus_data["transdate"].apply(lambda z: datetime.datetime.strptime(z, 
                                                                    strtime_format))
            cus_data["diff_time"] = cus_data["datetime_object"] - cus_data["datetime_object"].shift(-1)
            cus_data["time_interval"] = cus_data["diff_time"].apply(lambda z: - z.total_seconds())
            cus_data = cus_data.dropna()
            # cus_data = cus_data.set_index("coupled_transid")
            # cus_data = cus_data["time_interval"]
            coupled_transid_List = cus_data["coupled_transid"].to_list()
            time_interval_List = cus_data["time_interval"].to_list()
            cus_data = (coupled_transid_List, time_interval_List)
        return cus_data
    
    def build_dataframe_for_TIM(self, cus_data, window_size, is_detected_by_MBL):
        transformed_cus_data = []
        if is_detected_by_MBL:
            for comb, ti_arr in cus_data.items():
                (matchid, bettype, liveindicator) = comb
                if len(ti_arr) - window_size > 0:
                    for jj in range(len(ti_arr) - window_size + 1):
                        record = {"matchid":matchid, "bettype":bettype, "liveindicator":liveindicator}
                        for kk in range(1, window_size + 1):
                            record[f"dimension_{kk}"] = ti_arr[jj + kk - 1]
                        transformed_cus_data.append(record)
        else:
            coupled_transid_List, time_interval_List = cus_data
            # for coupled_transid, ti in cus_data.items():
            for jj in range(len(time_interval_List) - window_size + 1):
                sequence_Characterized = coupled_transid_List[jj : jj + window_size + 1]
                sequence_Characterized = "_".join(sequence_Characterized)
                sequence_Characterized = sequence_Characterized.split("_")
                sequence_Characterized = [int(x) for x in sequence_Characterized]
                sequence_Characterized = set(sequence_Characterized)
                sequence_Characterized = [str(x) for x in sequence_Characterized]
                sequence_Characterized = "_".join(sequence_Characterized)
                record = {"sequence_Characterized" : sequence_Characterized}
                for kk in range(1, window_size + 1): 
                    # sequence_Characterized += coupled_transid_List[jj + kk - 1]
                    record[f"dimension_{kk}"] = time_interval_List[jj + kk - 1]
                transformed_cus_data.append(record)
                
        transformed_cus_data = pd.DataFrame(transformed_cus_data)
        return transformed_cus_data
    
    def get_Time_Interval_Matrix(self, transformed_cus_data, is_detected_by_MBL):
        """
        >>> Input : aries | dataframe represents all dimensions and where they belong to
        """
        try:
            if is_detected_by_MBL:
                X = transformed_cus_data.iloc[:, [x for x in range(3, transformed_cus_data.shape[1])]].values
            else:
                X = transformed_cus_data.iloc[:, [x for x in range(1, transformed_cus_data.shape[1])]].values
            X = np.sort(X, axis = 1)
            max_by_row = np.max(X, axis = 1)
            max_by_row = np.expand_dims(max_by_row, axis = 1)
            X = X/max_by_row
            X = X[:, :-1] # this step needed because the last column = 1 for all rows
        except  ValueError:
            X = None
        return X
    
    def run(self, window_size, strtime_format, data, is_detected_by_MBL):
        cus_data = self.build_dictionary_pre_TIM(strtime_format, data, is_detected_by_MBL)
        transformed_cus_data = self.build_dataframe_for_TIM(cus_data, window_size, is_detected_by_MBL)
        X = self.get_Time_Interval_Matrix(transformed_cus_data, is_detected_by_MBL)
        return X, transformed_cus_data