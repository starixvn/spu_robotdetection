import pandas as pd
import os
import json
import logging
import time
from tqdm import tqdm
from Configuration.Configuration import config
from Utilities.Data_verification import Data_Verification
from Utilities.Supplementary_rules import Supplementary_rules
from Utilities.Prepare_data_for_each_user import Prepare_Data_for_each_user
from Utilities.Projection_2D import Projection_2D
from Utilities.Clustering_by_DBSCAN import Clustering_by_DBSCAN
from DataAccess.DataAccessConnection import spu_aiml
from DataAccess.DataAccessConnection import DataAccessConnection
from DataAccess.Model.SPU_AIML.SPU_InsertRobotUsersDAModel import SPU_InsertRobotUsersDAModel
from DataAccess.CoreDA.BaseDA import BaseDA

class Robot_Detection_Manager():

    @staticmethod
    def create_necessary_folders(day):
        try:
            os.makedirs(config.root + config.results + day)
            os.makedirs(config.root + config.results + day + "/" + config.quickly_test)
            if not config.is_save_all_in_one:
                os.makedirs(config.root + config.results + day + "/" + config.small_total_var)
                os.makedirs(config.root + config.results + day + "/" + config.big_total_var)
                os.makedirs(config.root + config.results + day + "/" + config.more_than_one_cluster_good)
                os.makedirs(config.root + config.results + day + "/" + config.more_than_one_cluster_pretty)
        except FileExistsError:
            pass
    
    @staticmethod
    def insert_robot_user_to_DB(full_info_all_user, day):
        connection_spu = DataAccessConnection(spu_aiml)
        chunks = [full_info_all_user[x:x + config.chunk_size] for x in \
                    range(0, len(full_info_all_user), config.chunk_size)]
        if config.insert_to_aiml:
            for chunk in chunks:
                chunk = json.dumps(chunk)
                ip_param = SPU_InsertRobotUsersDAModel(chunk, day)
                BaseDA.execute("SPU_AIML_InsertRobotUsers", spu_aiml, ip_param, connection_spu)

    @staticmethod
    def prepare_data(data_file):
        day = data_file.split(".")[0]
        Robot_Detection_Manager.create_necessary_folders(day)          
        data = pd.read_csv(config.root + config.data_path + data_file)
        data = data.sort_values("transdate")
        data = data.reset_index(drop = True)
        ls = data.custid.unique()
        return day, ls, data, []
    
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
            best_combination, others_for_reference = quickly_test_outcomes
            (matchid, bettypeid, is_live) = best_combination
            gonna_be_inserted_to_DB_data = {"C":int(custid), "M":matchid, "B":bettypeid, "LI":is_live, 
                                            "ISP":"", "DM":"", "TS":others_for_reference}
        return gonna_be_inserted_to_DB_data, best_combination

    @staticmethod
    def run():
        start_running = time.time()
        logging.basicConfig(filename =  config.root + config.save_dir_log + config.log_name, level = logging.INFO)
        data_files = sorted(os.listdir(config.root + config.data_path))
        for data_file in data_files[24:25]:
            day, ls, data, full_info_all_user = Robot_Detection_Manager.prepare_data(data_file)
            for custid in tqdm(ls, desc = f"Robot Detection is running for {day}"):
                preparator = Prepare_Data_for_each_user(custid)
                X, transformed_cus_data, cus_data = preparator.run(config.window_size, "%Y-%m-%d %H:%M:%S.%f", data, config.is_clustered_by_MBL)
                gonna_be_inserted_to_DB_data, best_combination = Robot_Detection_Manager.quickly_test_for_a_user(custid, transformed_cus_data, 
                                                                                                                cus_data, config.quickly_test_by_MBL)
                if gonna_be_inserted_to_DB_data is None:
                    gonna_be_inserted_to_DB_data = Robot_Detection_Manager.do_cluster_for_a_user(custid, data, day, X, transformed_cus_data)
                    if gonna_be_inserted_to_DB_data is None:
                        continue
                else:
                    Data_Verification.get_CSV_format_data(custid, day, data, best_combination, None, None, config, quickly_test_running = 1)
                full_info_all_user.append(gonna_be_inserted_to_DB_data)
            Robot_Detection_Manager.insert_robot_user_to_DB(full_info_all_user, day)
            print("\nNumber of robot users for %s has been added is %s\n" % (day, len(full_info_all_user)))
        print("\nTOTAL IMPLEMENTATION TIME = %.0f seconds" % (time.time() - start_running))