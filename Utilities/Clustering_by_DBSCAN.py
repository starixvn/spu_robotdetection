import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_samples
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
    def do_cluster(radius, min_samples, X):
        clustering = DBSCAN(eps = radius, min_samples = min_samples).fit(X)
        labels = clustering.labels_
        return labels
    
    @staticmethod
    def compute_performance_metric(data, is_single_pattern):
        if is_single_pattern:
            pca_df = data
            clustered_data = pca_df[pca_df.clustering_labels == 0]
            clustered_data = clustered_data[[0, 1]].values
            var_dim0, var_dim1 = np.var(clustered_data[:, 0]), np.var(clustered_data[:, 1])
            total_var = var_dim0 + var_dim1
            output = (total_var, 0)
        else:
            (projected_data, labels) = data
            projected_data = projected_data[labels != -1]
            labels = labels[labels != -1]
            sample_silhouette_values = silhouette_samples(projected_data, labels)
            bb = {k:np.median(sample_silhouette_values[labels == k]) for k in labels}               
            best_index = max(bb, key = bb.get)
            silhouette_score = bb[best_index]
            output = (silhouette_score, best_index)
        return output
    
    @staticmethod
    def get_data_for_verification(best_combination, custid, day, data, pca_df, pca_dict, information, is_single_pattern, config):
        (matchid, bettypeid, is_live) = best_combination
        aries = data[(data.matchid == matchid) & (data.bettype == bettypeid) 
                            & (data.liveindicator == is_live) & (data.custid == custid)][["transdate", "sporttype"]]
        performance_metric = information[0]
        plt.figure(figsize = (15, 8))
        plt.xlabel("Dimension 0", fontsize = 20)
        plt.ylabel("Dimension 1", fontsize = 20)
        sns.scatterplot(x = 0, y = 1, data = pca_df, s = 100, hue = "clustering_labels")
        for idx, coordindates in pca_dict.items():
            plt.text(coordindates[0] + .01, coordindates[1] + .01, idx, fontsize = 20)
        if is_single_pattern:
            plt.title("total_var = %.6f |radius = %.4f | min_samples = %s" % information, fontsize = 30)
            if performance_metric < config.decisive_total_var:
                is_robot = True
                aries.to_csv(config.results + day +  "/" + config.small_total_var + str(custid) + ".csv", index = False)              
                plt.savefig(config.results + day +  "/" + config.small_total_var + str(custid))
            else:
                is_robot = False
                aries.to_csv(config.results + day +  "/" + config.big_total_var + str(custid) + ".csv", index = False)
                plt.savefig(config.results + day +  "/" + config.big_total_var + str(custid))
        else:
            plt.title("Max_silhouette_score = %.4f | radius = %.4f | min_samples = %s" % information, fontsize = 30)
            if performance_metric > config.decisive_threshold:
                is_robot = True
                aries.to_csv(config.results + day +  "/" + config.more_than_one_cluster_good + str(custid) + ".csv", index = False)
                plt.savefig(config.results + day +  "/" + config.more_than_one_cluster_good + str(custid))
            else:
                is_robot = False
                aries.to_csv(config.results + day +  "/" + config.more_than_one_cluster_pretty + str(custid) + ".csv", index = False)
                plt.savefig(config.results + day +  "/" + config.more_than_one_cluster_pretty + str(custid))
        plt.close()
        return is_robot
    
    @staticmethod
    def get_best_combination(pca_df, aries, best_index):
        wish_list = pca_df[pca_df.clustering_labels == best_index].index.to_list()
        aries = aries.iloc[wish_list, :]
        aa = aries.groupby(["matchid", "bettype", "liveindicator"]).size().to_dict()
        best_combination = max(aa, key = aa.get)
        return best_combination

    @staticmethod
    def process_results(data, aries, day, custid, pca_df, pca_dict, projected_data, labels, radius, config):
        full_info_robot_user = None
        pca_df["clustering_labels"] = labels
        if np.prod(labels) == 0:
            if len(np.unique(labels)) < 2 or ((len(np.unique(labels)) == 2) and -1 in labels):
                is_single_pattern = 1
                performance_metric, best_index = Clustering_by_DBSCAN.compute_performance_metric(pca_df, 1)
                information = (performance_metric, radius, config.min_samples)
                best_combination = Clustering_by_DBSCAN.get_best_combination(pca_df, aries, best_index)
            else:
                is_single_pattern = 0                
                performance_metric, best_index = Clustering_by_DBSCAN.compute_performance_metric((projected_data, labels), 0)
                information = (performance_metric, radius, config.min_samples)
                best_combination = Clustering_by_DBSCAN.get_best_combination(pca_df, aries, best_index)
            is_robot = Clustering_by_DBSCAN.get_data_for_verification(best_combination, custid, day, data, pca_df,
                                                                        pca_dict, information, is_single_pattern, config)
            (matchid, bettypeid, is_live) = best_combination
            if is_robot:
                full_info_robot_user = {"C":int(custid), "M":matchid, "B":bettypeid, "LI":is_live, 
                                        "ISP":is_single_pattern, "DM":performance_metric}

        return full_info_robot_user
    
    @staticmethod
    def run(data, transformed_cus_data, day, custid, projected_data, pca_df, pca_dict, config):
        _, m2 = Clustering_by_DBSCAN.k_distances2(projected_data, config.min_samples)
        _1st_grad_arr, _2nd_grad_arr = Clustering_by_DBSCAN.compute_1st_and_2nd_derivative(m2)
        results = Clustering_by_DBSCAN.calculate_curvature(m2, _1st_grad_arr, _2nd_grad_arr)
        radius = Clustering_by_DBSCAN.decide_appropriate_radius(results, config.num_outstanding)
        labels = Clustering_by_DBSCAN.do_cluster(radius, config.min_samples, projected_data)
        full_info_robot_user = Clustering_by_DBSCAN.process_results(data, transformed_cus_data, day, custid, 
                                                                    pca_df, pca_dict, projected_data, labels, radius, config)
        return full_info_robot_user