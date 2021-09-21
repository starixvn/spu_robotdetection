import numpy as np
import datetime
import pandas as pd
import random
import logging
from Configuration.Configuration import config
from Helper.notify import Telegram_send_message

class Prepare_Data_for_each_user():
    def __init__(self, custid):
        self.custid = custid
        
    def convert_datetime_to_seconds(self, list_of_strtime, strtime_format):
        try:
            time_interval_arr = []
            for ii in range(1, len(list_of_strtime)):
                xx = datetime.datetime.strptime(list_of_strtime[ii], strtime_format)
                x = datetime.datetime.strptime(list_of_strtime[ii - 1], strtime_format)
                time_interval_arr.append((xx - x).total_seconds())
            return time_interval_arr
        except Exception as e:
            message = "%s | %s | ERROR | phase Insights_Extraction_by_Users | stage Data_Preparation | function convert_datetime_to_seconds : %s %s" % (config.app_name, 
                                                                                                                                                        config.ENV, 
                                                                                                                                                        type(e).__name__, 
                                                                                                                                                        e.args)
            print(message)
            logging.error(message)
            if config.agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError

    
    def build_dictionary_pre_TIM(self, strtime_format, data):
        try:
            cus_data_with_MBL = data[data.custid == self.custid][["custid", "transdate", "matchid", 
                                                        "bettype", "liveindicator"]]
            cus_data_with_MBL = cus_data_with_MBL.groupby(["matchid", "bettype", "liveindicator"])["transdate"] \
                    .agg(lambda z: sorted(list(z)))
            cus_data_with_MBL = cus_data_with_MBL.apply(lambda z: self.convert_datetime_to_seconds(z, strtime_format))
            cus_data_ignore_MBL = data[data.custid == self.custid][["custid", "transdate", "transid"]]
            cus_data_ignore_MBL = cus_data_ignore_MBL.sort_values("transdate")
            cus_data_ignore_MBL["coupled_transid"] = cus_data_ignore_MBL["transid"].map(str) + "_" + cus_data_ignore_MBL["transid"].map(str).shift(-1)
            cus_data_ignore_MBL["datetime_object"] = cus_data_ignore_MBL["transdate"].apply(lambda z: datetime.datetime.strptime(z, strtime_format))                                                                                                                                   
            cus_data_ignore_MBL["diff_time"] = cus_data_ignore_MBL["datetime_object"] - cus_data_ignore_MBL["datetime_object"].shift(-1)
            cus_data_ignore_MBL["time_interval"] = cus_data_ignore_MBL["diff_time"].apply(lambda z: - z.total_seconds())
            cus_data_ignore_MBL = cus_data_ignore_MBL.dropna()
            coupled_transid_List = cus_data_ignore_MBL["coupled_transid"].to_list()
            time_interval_List = cus_data_ignore_MBL["time_interval"].to_list()
            cus_data_ignore_MBL = (coupled_transid_List, time_interval_List)
            return (cus_data_with_MBL, cus_data_ignore_MBL)
        except Exception as e:
            message = "%s | %s | ERROR | phase Insights_Extraction_by_Users | stage Data_Preparation | function build_dictionary_pre_TIM : %s %s" % (config.app_name, 
                                                                                                                                                    config.ENV, 
                                                                                                                                                    type(e).__name__, 
                                                                                                                                                    e.args)
            print(message)
            logging.error(message)
            if config.agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def build_dataframe_for_TIM(self, cus_data, window_size, is_clustered_by_MBL):
        try:
            transformed_cus_data = []
            if is_clustered_by_MBL:
                cus_data = cus_data[0]
                for comb, ti_arr in cus_data.items():
                    (matchid, bettype, liveindicator) = comb
                    if len(ti_arr) - window_size > 0:
                        for jj in range(len(ti_arr) - window_size + 1):
                            record = {"matchid":matchid, "bettype":bettype, "liveindicator":liveindicator}
                            for kk in range(1, window_size + 1):
                                record[f"dimension_{kk}"] = ti_arr[jj + kk - 1]
                            transformed_cus_data.append(record)
            else:
                coupled_transid_List, time_interval_List = cus_data[1]
                for jj in range(len(time_interval_List) - window_size + 1):
                    sequence_Characterized = coupled_transid_List[jj : jj + window_size + 1]
                    sequence_Characterized = "_".join(sequence_Characterized)
                    sequence_Characterized = sequence_Characterized.split("_")
                    sequence_Characterized = set(sequence_Characterized)
                    sequence_Characterized = "_".join(sequence_Characterized)
                    record = {"sequence_Characterized" : sequence_Characterized}
                    for kk in range(1, window_size + 1): 
                        record[f"dimension_{kk}"] = time_interval_List[jj + kk - 1]
                    transformed_cus_data.append(record)
            random.shuffle(transformed_cus_data)      
            transformed_cus_data = pd.DataFrame(transformed_cus_data)
            return transformed_cus_data
        except Exception as e:
            message = "%s | %s | ERROR | phase Insights_Extraction_by_Users | stage Data_Preparation | function build_dataframe_for_TIM : %s %s" % (config.app_name, 
                                                                                                                                                    config.ENV, 
                                                                                                                                                    type(e).__name__, 
                                                                                                                                                    e.args)
            print(message)
            logging.error(message)
            if config.agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def get_Time_Interval_Matrix(self, transformed_cus_data, is_clustered_by_MBL):
        """
        >>> Input : aries | dataframe represents all dimensions and where they belong to
        """
        try:
            if len(transformed_cus_data) > 0:
                if is_clustered_by_MBL:
                    X = transformed_cus_data.iloc[:, [x for x in range(3, transformed_cus_data.shape[1])]].values
                else:
                    X = transformed_cus_data.iloc[:, [x for x in range(1, transformed_cus_data.shape[1])]].values
                X = np.sort(X, axis = 1)
                max_by_row = np.max(X, axis = 1)
                max_by_row = np.expand_dims(max_by_row, axis = 1)
                X = X/max_by_row
                X = X[:, :-1] # this step needed because the last column = 1 for all rows
                return X
            else:
                return None
        except Exception as e:
            message = "%s | %s | ERROR | phase Insights_Extraction_by_Users | stage Data_Preparation | function get_Time_Interval_Matrix : %s %s" % (config.app_name, 
                                                                                                                                                    config.ENV, 
                                                                                                                                                    type(e).__name__, 
                                                                                                                                                    e.args)
            print(message)
            logging.error(message)
            if config.agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
        
    
    def run(self, window_size, strtime_format, data, is_new_method, is_clustered_by_MBL):
        cus_data = self.build_dictionary_pre_TIM(strtime_format, data)
        if is_new_method:
            return None, None, cus_data
        else:
            transformed_cus_data = self.build_dataframe_for_TIM(cus_data, window_size, is_clustered_by_MBL)
            X = self.get_Time_Interval_Matrix(transformed_cus_data, is_clustered_by_MBL)
            return X, transformed_cus_data, cus_data