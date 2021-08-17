import matplotlib.pyplot as plt
import seaborn as sns
class Data_Verification():
    @staticmethod
    def get_visual_data(custid, day, pca_df, is_single_pattern, performance_metric, radius, min_samples, config):
        plt.figure(figsize = (15, 8))
        plt.xlabel("Dimension 0", fontsize = 20)
        plt.ylabel("Dimension 1", fontsize = 20)
        sns.scatterplot(x = 0, y = 1, data = pca_df, s = 100, hue = "clustering_labels")
        if not config.is_save_all_in_one:
            if is_single_pattern:
                plt.title("Ratio_TVR = %.6f |radius = %.4f | min_samples = %s" % (performance_metric, radius, min_samples), fontsize = 30)
                if performance_metric < config.decisive_TV_lv1:              
                        plt.savefig(config.root + config.results + day +  "/" + config.small_total_var + str(custid))
                elif (performance_metric < config.decisive_TV_lv2) and \
                    (performance_metric > config.decisive_TV_lv1):
                        plt.savefig(config.root + config.results + day +  "/" + config.big_total_var + str(custid))
            else:
                plt.title("Max_silhouette_score = %.4f | radius = %.4f | min_samples = %s" % (performance_metric, radius, min_samples), fontsize = 30)
                if performance_metric > config.decisive_MaSS_lv1:
                        plt.savefig(config.root + config.results + day +  "/" + config.more_than_one_cluster_good + str(custid))
                elif (performance_metric > config.decisive_MaSS_lv2) and \
                    (performance_metric < config.decisive_MaSS_lv1):
                        plt.savefig(config.root + config.results + day +  "/" + config.more_than_one_cluster_pretty + str(custid))
        else:             
            plt.savefig(config.root + config.results + day +  "/" + str(custid))
        plt.close()
    
    @staticmethod
    def get_CSV_format_data(custid, day, data, best_combination, is_single_pattern, performance_metric, config):
        desired_cols = ["matchid", "bettype", "liveindicator", "transdate", "sporttype"]
        if config.is_detected_by_MBL:
            (matchid, bettypeid, is_live) = best_combination
            verified_data = data[(data.matchid == matchid) & (data.bettype == bettypeid) 
                                & (data.liveindicator == is_live) & (data.custid == custid)][desired_cols]
        else:
            verified_data = data[data.transid.isin(best_combination)][desired_cols]
        if not config.is_save_all_in_one:
            if is_single_pattern:
                if performance_metric < config.decisive_TV_lv1:
                        verified_data.to_csv(config.root + config.results + day +  "/" + config.small_total_var + str(custid) + ".csv", index = False)              
                elif (performance_metric < config.decisive_TV_lv2) and \
                    (performance_metric > config.decisive_TV_lv1):                    
                        verified_data.to_csv(config.root + config.results + day +  "/" + config.big_total_var + str(custid) + ".csv", index = False)
            else:
                if performance_metric > config.decisive_MaSS_lv1:
                    verified_data.to_csv(config.root + config.results + day +  "/" + config.more_than_one_cluster_good + str(custid) + ".csv", index = False)
                elif (performance_metric > config.decisive_MaSS_lv2) and \
                    (performance_metric < config.decisive_MaSS_lv1):
                    verified_data.to_csv(config.root + config.results + day +  "/" + config.more_than_one_cluster_pretty + str(custid) + ".csv", index = False)
        else:
            verified_data.to_csv(config.root + config.results + day +  "/" + str(custid) + ".csv", index = False) 