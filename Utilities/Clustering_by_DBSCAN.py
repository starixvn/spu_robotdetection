import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_samples
from Utilities.Data_verification import Data_Verification
import warnings
warnings.filterwarnings("ignore")
class Clustering_by_DBSCAN():
    
    @staticmethod
    def k_distances2(x, k):
        dim0 = x.shape[0]
        p = -2*x.dot(x.T) + np.sum(x**2, axis = 1).T + np.repeat(np.sum(x**2, axis = 1), dim0, axis = 0) \
            .reshape(dim0,dim0)
        p = np.sqrt(p)
        p.sort(axis = 1)
        p = p[:, :k]
        pm = p.flatten()
        pm = np.sort(pm)
        return p, pm
    
    @staticmethod
    def compute_curvature(_1st_grad, _2nd_grad):
        return _2nd_grad / (1 + _1st_grad*_1st_grad)**1.5
    
    @staticmethod
    def compute_1st_and_2nd_derivative(m2):
        k = len(m2)
        _1st_grad_arr = k*(m2[1:] - m2[:-1])
        _2nd_grad_arr = (k - 1)*(_1st_grad_arr[1:] - _1st_grad_arr[:-1])
        return _1st_grad_arr, _2nd_grad_arr
    
    @staticmethod
    def calculate_curvature(m2, _1st_grad_arr, _2nd_grad_arr):
        results = []
        for ii in range(int(len(_2nd_grad_arr)/2), len(_2nd_grad_arr)):
            _1st_grad = _1st_grad_arr[ii]
            _2nd_grad = _2nd_grad_arr[ii]
            curvature = Clustering_by_DBSCAN.compute_curvature(_1st_grad, _2nd_grad)
            results.append((ii, curvature, m2[ii]))
        return results
    
    @staticmethod
    def decide_appropriate_radius(results, num_outstanding):
        top = sorted(results, key = lambda x: x[1], reverse = True)[:num_outstanding]
        radius = sorted(top, key = lambda x: x[0])[0][-1]
        return radius
    
    @staticmethod
    def do_cluster(pca_df, radius, min_samples, X):
        clustering = DBSCAN(eps = radius, min_samples = min_samples).fit(X)
        labels = clustering.labels_
        pca_df["clustering_labels"] = labels
        return pca_df, labels
    
    @staticmethod
    def compute_performance_metric(projected_data, labels, is_single_pattern, radius):
        well_clustered_data = projected_data[labels != -1]
        labels = labels[labels != -1]
        if is_single_pattern:
            var_dim0, var_dim1 = np.var(well_clustered_data[:, 0]), np.var(well_clustered_data[:, 1])
            total_var = var_dim0 + var_dim1
            ratio_TotalVar_Radius = total_var / radius
            output = (ratio_TotalVar_Radius, 0)
        else:            
            sample_silhouette_values = silhouette_samples(well_clustered_data, labels)
            bb = {k:np.median(sample_silhouette_values[labels == k]) for k in labels}               
            best_index = max(bb, key = bb.get)
            silhouette_score = bb[best_index]
            output = (silhouette_score, best_index)
        return output
    
    @staticmethod
    def is_user_robot(performance_metric, is_single_pattern, config):   
        is_robot = False   
        if is_single_pattern:
            if performance_metric < config.decisive_TV_lv1:
                is_robot = True
            elif (performance_metric < config.decisive_TV_lv2) and \
                (performance_metric > config.decisive_TV_lv1):
                is_robot = False
        else:
            if performance_metric > config.decisive_MaSS_lv1:
                is_robot = True
            elif (performance_metric > config.decisive_MaSS_lv2) and \
                (performance_metric < config.decisive_MaSS_lv1):
                is_robot = False
        return is_robot
    
    @staticmethod
    def get_best_combination(pca_df, transformed_cus_data, best_index, is_clustered_by_MBL):
        wish_list = pca_df[pca_df.clustering_labels == best_index].index.to_list()
        wished_data = transformed_cus_data.iloc[wish_list, :]
        if is_clustered_by_MBL:
            aa = wished_data.groupby(["matchid", "bettype", "liveindicator"]).size().to_dict()
            best_combination = max(aa, key = aa.get)
        else:
            best_combination = wished_data["sequence_Characterized"].to_list()
            best_combination = "_".join(best_combination)
            best_combination = best_combination.split("_")
            best_combination = [int(x) for x in best_combination]
            best_combination = set(best_combination)
        return best_combination
    
    @staticmethod
    def generate_data_to_Insert_DB(custid, full_info_robot_user, is_clustered_by_MBL):      
        gonna_be_inserted_to_DB_data = None
        if full_info_robot_user is not None:
            is_robot, best_combination, is_single_pattern, performance_metric, _, _, _ = full_info_robot_user
            if is_robot:
                if is_clustered_by_MBL:
                    (matchid, bettypeid, is_live) = best_combination
                    gonna_be_inserted_to_DB_data = {"C":int(custid), "M":matchid, "B":bettypeid, "LI":is_live, 
                                                    "ISP":is_single_pattern, "DM":performance_metric, "TS":""}
                else:
                    transID_sequence = ",".join([str(v) for v in best_combination])
                    gonna_be_inserted_to_DB_data = {"C":int(custid), "M":0, "B":0, "LI":0, 
                                                    "ISP":is_single_pattern, "DM":performance_metric, "TS":transID_sequence}
        return gonna_be_inserted_to_DB_data

    @staticmethod
    def get_data_for_verification(custid, day, pca_df, data, full_info_robot_user, config, quickly_test_running) :
        try:
            is_robot, best_combination, is_single_pattern, performance_metric, radius, min_samples, best_index = full_info_robot_user
            if is_robot:
                Data_Verification.get_visual_data(custid, day, pca_df, is_single_pattern, performance_metric, radius, min_samples, config, best_index)
                Data_Verification.get_CSV_format_data(custid, day, data, best_combination, is_single_pattern, performance_metric, config, quickly_test_running) 
        except TypeError:
            pass

    @staticmethod
    def validate_results(transformed_cus_data, pca_df, projected_data, labels, radius, config):
        full_info_robot_user = None
        if np.prod(labels) == 0:
            num_distinct_labels = len(np.unique(labels))
            if num_distinct_labels == 1 or (num_distinct_labels == 2 and -1 in labels):
                is_single_pattern = 1
            else:
                is_single_pattern = 0                
            performance_metric, best_index = Clustering_by_DBSCAN.compute_performance_metric(projected_data, labels, is_single_pattern, radius)
            best_combination = Clustering_by_DBSCAN.get_best_combination(pca_df, transformed_cus_data, best_index, config.is_clustered_by_MBL)
            is_robot = Clustering_by_DBSCAN.is_user_robot(performance_metric, is_single_pattern, config)            
            full_info_robot_user = (is_robot, best_combination, is_single_pattern, performance_metric, radius, config.min_samples, best_index)
        return full_info_robot_user
    
    @staticmethod
    def run(data, transformed_cus_data, day, custid, projected_data, pca_df, pca_dict, config):
        _, m2 = Clustering_by_DBSCAN.k_distances2(projected_data, config.min_samples)
        _1st_grad_arr, _2nd_grad_arr = Clustering_by_DBSCAN.compute_1st_and_2nd_derivative(m2)
        results = Clustering_by_DBSCAN.calculate_curvature(m2, _1st_grad_arr, _2nd_grad_arr)
        radius = Clustering_by_DBSCAN.decide_appropriate_radius(results, config.num_outstanding)
        pca_df, labels = Clustering_by_DBSCAN.do_cluster(pca_df, radius, config.min_samples, projected_data)
        full_info_robot_user = Clustering_by_DBSCAN.validate_results(transformed_cus_data, pca_df, projected_data, labels, radius, config)
        Clustering_by_DBSCAN.get_data_for_verification(custid, day, pca_df, data, full_info_robot_user, config, 0)
        gonna_be_inserted_to_DB_data = Clustering_by_DBSCAN.generate_data_to_Insert_DB(custid, full_info_robot_user, config.is_clustered_by_MBL)                                                                                                           
        return gonna_be_inserted_to_DB_data