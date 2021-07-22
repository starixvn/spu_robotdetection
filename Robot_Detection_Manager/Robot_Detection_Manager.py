import pandas as pd
import os
import json
import logging
import time
from tqdm import tqdm
from Configuration.Configuration import config
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
            os.makedirs(config.results + day)
            os.makedirs(config.results + day + "/" + config.small_total_var)
            os.makedirs(config.results + day + "/" + config.big_total_var)
            os.makedirs(config.results + day + "/" + config.more_than_one_cluster_good)
            os.makedirs(config.results + day + "/" + config.more_than_one_cluster_pretty)
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
    def run():
        start_running = time.time()
        logging.basicConfig(filename = config.save_dir_log + config.log_name, level = logging.INFO)
        data_files = sorted(os.listdir(config.data_path))
        for data_file in data_files[:1]:
            full_info_all_user = []
            day = data_file.split(".")[0]
            Robot_Detection_Manager.create_necessary_folders(day)          
            data = pd.read_csv(config.data_path + data_file)
            ls = data.custid.unique()
            for custid in tqdm(ls, desc = f"Robot Detection is running for {day}"):
                preparator = Prepare_Data_for_each_user(custid)
                X, transformed_cus_data = preparator.run(config.window_size, "%Y-%m-%d %H:%M:%S.%f", data)
                if X is None:
                    continue
                if X.shape[0] < config.window_size:
                    continue
                projected_data, pca_df, pca_dict = Projection_2D.run(X)
                full_info_robot_user = Clustering_by_DBSCAN.run(data, transformed_cus_data, day, custid, projected_data, 
                                                                pca_df, pca_dict, config)
                if full_info_robot_user is None:
                    continue
                full_info_all_user.append(full_info_robot_user)
            Robot_Detection_Manager.insert_robot_user_to_DB(full_info_all_user, day)
            print("\nNumber of robot users for %s has been added is %s\n" % (day, len(full_info_all_user)))
        print("\nTOTAL IMPLEMENTATION TIME = %.0f seconds" % (time.time() - start_running))