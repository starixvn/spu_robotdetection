import pandas as pd
import os
import json
import logging
import time
import datetime
from tqdm import tqdm
from Configuration.Configuration import config
from Utilities.Data_verification import Data_Verification
from Utilities.Supplementary_rules import Supplementary_rules
from Utilities.Prepare_data_for_each_user import Prepare_Data_for_each_user
from Utilities.Projection_2D import Projection_2D
from Utilities.Clustering_by_DBSCAN import Clustering_by_DBSCAN
from DataAccess.DataAccessConnection import spu_aiml, cts_datacenter
from DataAccess.DataAccessConnection import DataAccessConnection
from Helper.notify import Telegram_send_message
from DataAccess.Model.SPU_AIML.SPU_RD_InsertRobotStatsDAModel import SPU_RD_InsertRobotStatsDAModel
from DataAccess.Model.CTS_DataCenter.CTS_DC_RobotDetection_InsertDAModel import CTS_DC_RobotDetection_InsertDAModel
from DataAccess.Model.SPU_AIML.SPU_AIML_RD_ComputeRobotUsersDAModel import SPU_AIML_RD_ComputeRobotUsersDAModel
from DataAccess.CoreDA.BaseDA import BaseDA
from Utilities.Utilities import assign_into_PeriodRange

class Robot_Detection_Manager():

    @staticmethod
    def create_necessary_folders(day):
        try:
            if config.data_for_verification_got_saved:
                os.makedirs(config.root + config.results + day)
                if config.is_detected_by_new_method:
                    os.makedirs(config.root + config.results + day + "/" + config.easy_to_see)
                    os.makedirs(config.root + config.results + day + "/" + config.hard_to_see)
                else:
                    os.makedirs(config.root + config.results + day + "/" + config.quickly_test)
                    if not config.is_save_all_in_one:
                        os.makedirs(config.root + config.results + day + "/" + config.small_total_var)
                        os.makedirs(config.root + config.results + day + "/" + config.big_total_var)
                        os.makedirs(config.root + config.results + day + "/" + config.more_than_one_cluster_good)
                        os.makedirs(config.root + config.results + day + "/" + config.more_than_one_cluster_pretty)
            else:
                pass
        except FileExistsError:
            pass
    
    # @staticmethod
    # def insert_robot_user_to_DB(full_info_all_user, day):
    #     connection_spu = DataAccessConnection(spu_aiml)
    #     chunks = [full_info_all_user[x:x + config.chunk_size] for x in \
    #                 range(0, len(full_info_all_user), config.chunk_size)]
    #     if config.insert_to_aiml:
    #         for chunk in chunks:
    #             chunk = json.dumps(chunk)
    #             ip_param = SPU_InsertRobotUsersDAModel(chunk, day)
    #             BaseDA.execute("SPU_AIML_InsertRobotUsers", spu_aiml, ip_param, connection_spu)
    @staticmethod
    def insert_robot_user_to_DB(full_info_all_user, day):
        try:
            connection_spu = DataAccessConnection(spu_aiml)
            chunks = [full_info_all_user[x:x + config.chunk_size] for x in \
                        range(0, len(full_info_all_user), config.chunk_size)]
            if config.insert_to_aiml:
                for chunk in chunks:
                    chunk = json.dumps(chunk)
                    ip_param = SPU_RD_InsertRobotStatsDAModel(chunk, day)
                    BaseDA.execute("SPU_AIML_RD_InsertRobotStats", spu_aiml, ip_param, connection_spu)
            #         results = BaseDA.execute("SPU_AIML_RD_InsertRobotStats", spu_aiml, ip_param, connection_spu)
            # return results
        except Exception as e:
            message = "%s | %s | ERROR | phase Interaction_with_SPU_DB | function insert_robot_user_to_DB : %s %s" % (config.app_name, 
                                                                                                                        config.ENV, 
                                                                                                                        type(e).__name__, 
                                                                                                                        e.args)
            print(message)
            logging.error(message)
            if config.agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError

    @staticmethod
    def compute_robot_for_pushing_to_CTS(day):
        try:
            connection_spu = DataAccessConnection(spu_aiml)
            # chunks = [full_info_all_user[x:x + config.chunk_size] for x in \
            #             range(0, len(full_info_all_user), config.chunk_size)]
            if config.insert_to_aiml:
                # for chunk in chunks:
                    # chunk = json.dumps(chunk)
                ip_param = SPU_AIML_RD_ComputeRobotUsersDAModel(day)
                results = BaseDA.execute("SPU_AIML_RD_ComputeRobotUsers", spu_aiml, ip_param, connection_spu)
                results = results[0]
                df = pd.DataFrame(results, columns = ["C", "R", "LR"])
                gonna_be_pushed_to_CTS = df.to_dict(orient = 'records')
                return gonna_be_pushed_to_CTS
        except Exception as e:
            message = "%s | %s | ERROR | phase Interaction_with_SPU_DB | function compute_robot_for_pushing_to_CTS : %s %s" % (config.app_name, 
                                                                                                                                config.ENV, 
                                                                                                                                type(e).__name__, 
                                                                                                                                e.args)
            print(message)
            logging.error(message)
            if config.agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    @staticmethod
    def insert_robot_user_to_CTS(full_info_all_user):
        try:
            connection_cts = DataAccessConnection(cts_datacenter)
            chunks = [full_info_all_user[x:x + config.chunk_size] for x in \
                        range(0, len(full_info_all_user), config.chunk_size)]
            if config.insert_to_cts:
                for chunk in chunks:
                    chunk = json.dumps(chunk)
                    ip_param = CTS_DC_RobotDetection_InsertDAModel(chunk)
                    BaseDA.execute("CTS_DC_RobotDetection_Insert", cts_datacenter, ip_param, connection_cts)
        except Exception as e:
            message = "%s | %s | ERROR | phase Interaction_with_CTS_DC | function insert_robot_user_to_CTS : %s %s" % (config.app_name, 
                                                                                                                        config.ENV, 
                                                                                                                        type(e).__name__, 
                                                                                                                        e.args)
            print(message)
            logging.error(message)
            if config.agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError

    # @staticmethod
    # def get_distinct_robot_user():
    #     connection_spu = DataAccessConnection(spu_aiml)
    #     ip_param = SPU_GetDistinctRobotUserDAModel()
    #     robot_users = BaseDA.execute("SPU_AIML_GetDistinctRobotUser", spu_aiml, ip_param, connection_spu)
    #     robot_users = robot_users[0] # List in List
    #     robot_users = [x[0] for x in robot_users] # [(21061103,), . . .]
    #     return robot_users

    @staticmethod
    # def prepare_data(data_files, day, is_used_full_data = True, limit = 500):
    def prepare_data(data_file, day):
        try:
            # day = data_file.split(".")[0]
            Robot_Detection_Manager.create_necessary_folders(day)          
            data = pd.read_csv(config.root + config.data_path + data_file)
            data = data.sort_values("transdate")
            data = data.reset_index(drop = True)
            ls = data.custid.unique()
            return ls, data, [], []
        except Exception as e:
            message = "%s | %s | ERROR | phase Reading_Data | function prepare_data : %s %s" % (config.app_name, 
                                                                                                config.ENV, 
                                                                                                type(e).__name__, 
                                                                                                e.args)
            print(message)
            logging.error(message)
            if config.agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    @staticmethod
    def check_constraints_for_clustering(X):
        if X is None:
            return False
        elif X.shape[0] < config.ratio_criteria*config.min_samples:
            return False
        else:
            return True
    
    @staticmethod
    def do_cluster_for_a_user(custid, data, day, X, transformed_cus_data):
        gonna_be_inserted_to_DB_data = None
        if Robot_Detection_Manager.check_constraints_for_clustering(X):
            projected_data, pca_df, pca_dict = Projection_2D.run(X)
            gonna_be_inserted_to_DB_data = Clustering_by_DBSCAN.run(data, transformed_cus_data, day, custid, projected_data, 
                                                                    pca_df, pca_dict, config)
        return gonna_be_inserted_to_DB_data
    
    @staticmethod
    def quickly_test_for_a_user(custid, transformed_cus_data, cus_data, quickly_test_by_MBL):      
        gonna_be_inserted_to_DB_data, best_combination = None, None
        quickly_test_outcomes = Supplementary_rules.is_Ticket_placement_so_fast(transformed_cus_data, cus_data, quickly_test_by_MBL)
        if quickly_test_outcomes is not None:
            if quickly_test_by_MBL:
                best_combination, others_for_reference = quickly_test_outcomes
                (matchid, bettypeid, is_live) = best_combination
                gonna_be_inserted_to_DB_data = {"C":int(custid), "M":matchid, "B":bettypeid, "LI":is_live, 
                                                "ISP":"", "DM":"", "TS":others_for_reference}
            else:
                # print("best_combination = %s" % best_combination)
                best_combination = quickly_test_outcomes
                gonna_be_inserted_to_DB_data = {"C":int(custid), "M":0, "B":0, "LI":0, 
                                                "ISP":"", "DM":"", "TS":best_combination}
        return gonna_be_inserted_to_DB_data, best_combination
    
    @staticmethod
    def detect_by_Old_method(day, ls, data, full_info_all_user, is_clustered_by_MBL, is_save_all_in_one):
        for custid in tqdm(ls, desc = f"Old Method - Clustered by MBL = {is_clustered_by_MBL} - Save all in one = {is_save_all_in_one} | Robot Detection is running for {day}"):
            preparator = Prepare_Data_for_each_user(custid)
            X, transformed_cus_data, cus_data = preparator.run(config.window_size, "%Y-%m-%d %H:%M:%S.%f", data, config.is_clustered_by_MBL)
            gonna_be_inserted_to_DB_data, best_combination = Robot_Detection_Manager.quickly_test_for_a_user(custid, transformed_cus_data, 
                                                                                                            cus_data, config.quickly_test_by_MBL)
            if gonna_be_inserted_to_DB_data is None:
                gonna_be_inserted_to_DB_data = Robot_Detection_Manager.do_cluster_for_a_user(custid, data, day, X, transformed_cus_data)
                if gonna_be_inserted_to_DB_data is None:
                    continue
            else:
                Data_Verification.get_CSV_format_data(custid, day, data, best_combination, None, None, config, 1)
            full_info_all_user.append(gonna_be_inserted_to_DB_data)
        return full_info_all_user

    @staticmethod
    def detect_by_New_method(day, ls, data, full_info_all_user_TableA, full_info_all_user_TableB, 
                            minimum_suspicious_transID, data_for_verification_got_saved, is_assigned_to_PeriodRange = 0):
        try:
            for custid in tqdm(ls, desc = f"New Method | Robot Detection is running for {day}"):
                preparator = Prepare_Data_for_each_user(custid)
                _, _, cus_data = preparator.run(config.window_size, 
                                                "%Y-%m-%d %H:%M:%S.%f", 
                                                data,
                                                config.is_detected_by_new_method, 
                                                config.is_clustered_by_MBL)
                extraordinary_signal = 0

                # ============================ Used for debug ============================
                # if custid == 44839688:
                #     extraordinary_signal = 1
                # ============================ Used for debug ============================

                detecting_outcomes = Supplementary_rules.detect_by_TSSM(cus_data, config.based_on_STD, extraordinary_signal)
                if detecting_outcomes is None:
                    continue
                best_combination, easy_to_see, num_suspicious_transID, period_chain, robot_stats_info = detecting_outcomes
                if num_suspicious_transID <= minimum_suspicious_transID:
                    continue
                if is_assigned_to_PeriodRange:
                    # gonna_be_inserted_to_TableA_data, gonna_be_inserted_to_TableB_data = assign_into_PeriodRange(custid, best_combination, 
                    #                                                                                             period_chain, robot_stats_info)
                    gonna_be_inserted_to_DB_data = assign_into_PeriodRange(custid, best_combination, period_chain, robot_stats_info)
                                                                                                                
                    if extraordinary_signal:
                        # print("\ngonna_be_inserted_to_TableA_data = " + str(gonna_be_inserted_to_TableA_data),
                        #     "\ngonna_be_inserted_to_TableB_data = " + str(gonna_be_inserted_to_TableB_data))
                        print("\ngonna_be_inserted_to_DB_data = " + str(gonna_be_inserted_to_DB_data))
                            
                else:
                    gonna_be_inserted_to_DB_data = {"C":int(custid), "M":0, "B":0, "LI":0, 
                                                    "ISP":"", "DM":"", "TS":best_combination, "PC": period_chain}
                if data_for_verification_got_saved:
                    Data_Verification.get_CSV_format_data(custid, day, data, best_combination, None, None, config, 0, easy_to_see)
                # full_info_all_user_TableA.append(gonna_be_inserted_to_TableA_data)
                # full_info_all_user_TableB.append(gonna_be_inserted_to_TableB_data)
                full_info_all_user_TableA += gonna_be_inserted_to_DB_data
            # return full_info_all_user_TableA, full_info_all_user_TableB
            return full_info_all_user_TableA
        except Exception as e:
            message = "%s | %s | ERROR | phase Insights_Extraction_by_Users | function detect_by_New_method : %s %s" % (config.app_name, 
                                                                                                                        config.ENV, 
                                                                                                                        type(e).__name__, 
                                                                                                                        e.args)
            print(message)
            logging.error(message)
            if config.agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def check_aimed_directories(kind, day_in_new_format):
        try:
            partial_candidates = []
            aimed_directories = config.aimed_directories
            aimed_directory = aimed_directories[kind]
            group = os.listdir(aimed_directory)
            for fn in group:
                if fn.startswith("bettrans_" + day_in_new_format) and fn.endswith(".csv"):
                    partial_candidates.append(fn)
            # if len(candidates) > minimum_files:
            #     data = pd.concat([pd.read_csv(aimed_directory + fn, skipfooter = 1, skiprows = [1]) for fn in candidates]
            #                     , ignore_index = True)
            return partial_candidates, aimed_directory
        except Exception as e:
            message = "%s | %s | ERROR | phase Reading_Data | function check_aimed_directories : %s %s" % (config.app_name, 
                                                                                                            config.ENV, 
                                                                                                            type(e).__name__, 
                                                                                                            e.args)
            print(message)
            logging.error(message)
            if config.agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def generate_data(day, is_data_contained_in_a_single_file):
        try:
            print("day = " + day)
            datetime_object = datetime.datetime.strptime(day, '%Y-%m-%d')
            day_in_new_format = datetime_object.strftime('%m_%d_%Y')
            if config.ENV == "LOCAL":
                if is_data_contained_in_a_single_file:
                    num_files = 1
                    data = pd.read_csv(config.root + config.data_path + day + ".csv")
                else:
                    data_files = os.listdir(config.root + config.data_path)
                    candidates = []
                    for fn in data_files:
                        if fn.startswith("bettrans_" + day_in_new_format) and fn.endswith(".csv"):
                            candidates.append(fn)
                    num_files = len(candidates)
                    data = pd.concat([pd.read_csv(config.root + config.data_path + fn, skipfooter = 1, skiprows = [1]) for fn in candidates]
                                    , ignore_index = True)
            
            else:
                # total_candidates = []
                partial_candidates_1st, aimed_directory_1st = Robot_Detection_Manager.check_aimed_directories("1st", day_in_new_format)
                # total_candidates += partial_candidates
                # if data is None:
                partial_candidates_2nd, aimed_directory_2nd = Robot_Detection_Manager.check_aimed_directories("2nd", day_in_new_format)
                num_files = len(partial_candidates_1st) + len(partial_candidates_2nd)
                if num_files < config.minimum_files:
                    message = "%s | %s | ERROR | phase Reading_data | function generate_data : %s because of number of files < %s" % (config.app_name, 
                                                                                                                                    config.ENV, 
                                                                                                                                    "There is not enough data",
                                                                                                                                    config.minimum_files)
                    print(message)
                    logging.error(message)
                    if config.agree_to_send_message:
                        Telegram_send_message(message)
                    raise ValueError
                if len(partial_candidates_1st) > 0:
                    data_1st = pd.concat([pd.read_csv(aimed_directory_1st + fn, skipfooter = 1, skiprows = [1]) for fn in partial_candidates_1st], 
                                        ignore_index = True)
                else:
                    data_1st = pd.DataFrame()
                if len(partial_candidates_2nd) > 0:
                    data_2nd = pd.concat([pd.read_csv(aimed_directory_2nd + fn, skipfooter = 1, skiprows = [1]) for fn in partial_candidates_2nd], 
                                        ignore_index = True)
                else:
                    data_2nd = pd.DataFrame()
                data = pd.concat([data_1st, data_2nd], ignore_index = True)
                
            print("HEAD of data\n", data.head())
            print("TAIL of data\n", data.tail())
            data.to_csv(config.root + config.data_path + day + ".csv", index = False)
            return num_files
        except Exception as e:
            message = "%s | %s | ERROR | phase Reading_Data | function generate_data : %s %s" % (config.app_name, 
                                                                                                config.ENV, 
                                                                                                type(e).__name__, 
                                                                                                e.args)
            print(message)
            logging.error(message)
            if config.agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError

    @staticmethod
    def run(day = "", is_data_contained_in_a_single_file = 0):
        start_running = time.time()
        logging.basicConfig(filename =  config.root + config.save_dir_log + config.log_name, level = logging.INFO)
        now = datetime.datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        if day == "":
            today = now.strftime("%Y-%m-%d")
            datetime_object = datetime.datetime.strptime(today, '%Y-%m-%d')
            day = datetime_object + datetime.timedelta(days = - config.num_days_backward)
            day = day.strftime('%Y-%m-%d')
        message = "%s | %s | INFO | Running for %s" % (config.app_name, config.ENV, day)
        if config.agree_to_send_message:
            Telegram_send_message(message)
        message = f"======================================== {current_time} | Running for {day} ========================================"
        print(message)
        logging.info(message)     
        # data_files = sorted(os.listdir(config.root + config.data_path))
        # for data_file in data_files[:1]: # for quick test of programm
        # for data_file in data_files:
        # ls, data, full_info_all_user_TableA, full_info_all_user_TableB = Robot_Detection_Manager.prepare_data(data_files, day, True, 5000)
        num_files = Robot_Detection_Manager.generate_data(day, is_data_contained_in_a_single_file)
        ls, data, full_info_all_user_TableA, full_info_all_user_TableB = Robot_Detection_Manager.prepare_data(day + ".csv", day)
        if config.is_program_being_tested:
            ls = ls[:config.num_desired_to_test]
            data = data[data.custid.isin(ls)]
        message = "%s | %s | INFO | No. Files = %s | No. Transactions = %s | No. Customers = %s" % (config.app_name, 
                                                                                                    config.ENV,
                                                                                                    num_files, 
                                                                                                    len(data), 
                                                                                                    len(ls))
        if config.agree_to_send_message:
            Telegram_send_message(message)
        print(message)
        logging.info(message)     
        if config.is_detected_by_new_method:
            # full_info_all_user_TableA, full_info_all_user_TableB = Robot_Detection_Manager.detect_by_New_method(day, ls, data, 
            #                                                                                                     full_info_all_user_TableA,
            #                                                                                                     full_info_all_user_TableB, 
            #                                                                                                     config.minimum_suspicious_transID,
            #                                                                                                     config.is_assigned_to_PeriodRange)
            full_info_all_user = Robot_Detection_Manager.detect_by_New_method(  day, ls, data, 
                                                                                full_info_all_user_TableA,
                                                                                full_info_all_user_TableB, 
                                                                                config.minimum_suspicious_transID,
                                                                                config.data_for_verification_got_saved,
                                                                                config.is_assigned_to_PeriodRange
                                                                            )
        # else:
        #     full_info_all_user = Robot_Detection_Manager.detect_by_Old_method(day, ls, data, full_info_all_user, 
        #                                                                         config.is_clustered_by_MBL,
        #                                                                         config.is_save_all_in_one)
        # print("\nfull_info_all_user = " + str(full_info_all_user))
        Robot_Detection_Manager.insert_robot_user_to_DB(full_info_all_user, day)
        # print("\nNumber of Suspicious users for %s has been added is %s\n" % (day, len(full_info_all_user)))
        message = "%s | %s | INFO |  %s Suspicious users were pushed to SPU" % (config.app_name, config.ENV, len(full_info_all_user))
        if config.agree_to_send_message:
            Telegram_send_message(message)
        print(message)
        logging.info(message)
        gonna_be_pushed_to_CTS = Robot_Detection_Manager.compute_robot_for_pushing_to_CTS(day)
        # print("\ngonna_be_pushed_to_CTS = " + str(gonna_be_pushed_to_CTS))
        Robot_Detection_Manager.insert_robot_user_to_CTS(gonna_be_pushed_to_CTS)
        # print("\nNumber of robot users for %s has been pushed to CTS is %s\n" % (day, len(gonna_be_pushed_to_CTS)))
        #print("\nTOTAL IMPLEMENTATION TIME = %.0f seconds" % (time.time() - start_running))
        message = "%s | %s | INFO | Completed in %.2f seconds with %s robot users pushed to CTS" % (config.app_name, 
                                                                                                    config.ENV, 
                                                                                                    time.time() - start_running,
                                                                                                    len(gonna_be_pushed_to_CTS))
        if config.agree_to_send_message:
            Telegram_send_message(message)
        print(message)
        logging.info(message)
        now = datetime.datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        message = f"======================================== {current_time} | Done for {day} ========================================"
        print(message)
        logging.info(message)