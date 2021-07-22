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
    
    def build_dictionary_pre_TIM(self, strtime_format, data):
        cus_data = data[data.custid == self.custid][["custid", "transdate", "matchid", 
                                                  "bettype", "liveindicator"]]
        cus_data = cus_data.groupby(["matchid", "bettype", "liveindicator"])["transdate"] \
                .agg(lambda z: sorted(list(z)))
        cus_data = cus_data.apply(lambda z: self.convert_datetime_to_seconds(z, strtime_format))
        return cus_data
    
    def build_dataframe_for_TIM(self, cus_data, window_size):
        """
        >>> Input : harvey | Python dictionary
        """
        transformed_cus_data = []
        for comb, ti_arr in cus_data.items():
            (matchid, bettype, liveindicator) = comb
            if len(ti_arr) - window_size > 0:
                for jj in range(len(ti_arr) - window_size + 1):
                    record = {"matchid":matchid, "bettype":bettype, "liveindicator":liveindicator}
                    for kk in range(1, window_size + 1):
                        record[f"dimension_{kk}"] = ti_arr[jj + kk - 1]
                    transformed_cus_data.append(record)
        transformed_cus_data = pd.DataFrame(transformed_cus_data)
        return transformed_cus_data
    
    def get_Time_Interval_Matrix(self, aries):
        """
        >>> Input : aries | dataframe represents all dimensions and where they belong to
        """
        try:
            X = aries.iloc[:, [x for x in range(3, aries.shape[1])]].values
            X = np.sort(X, axis = 1)
            max_by_row = np.max(X, axis = 1)
            max_by_row = np.expand_dims(max_by_row, axis = 1)
            X = X/max_by_row
        except  ValueError:
            X = None
        return X
    
    def run(self, window_size, strtime_format, data):
        cus_data = self.build_dictionary_pre_TIM(strtime_format, data)
        transformed_cus_data = self.build_dataframe_for_TIM(cus_data, window_size)
        X = self.get_Time_Interval_Matrix(transformed_cus_data)
        return X, transformed_cus_data