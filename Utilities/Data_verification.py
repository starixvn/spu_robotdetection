import matplotlib.pyplot as plt
import seaborn as sns
class Data_Verification():
    @staticmethod
    def get_visual_data(custid, day, pca_df, is_single_pattern, performance_metric, radius, min_samples, config, best_index):
        plt.figure(figsize = (15, 8))
        plt.xlabel("Dimension 0", fontsize = 20)
        plt.ylabel("Dimension 1", fontsize = 20)
        sns.scatterplot(x = 0, y = 1, data = pca_df, s = 100, hue = "clustering_labels")
        plt.title("DM = %.6f | R = %.4f | MS = %s | BI = %s" % (performance_metric, radius, min_samples, best_index), fontsize = 30)
        if not config.is_save_all_in_one:
            if is_single_pattern:
                if performance_metric < config.decisive_TV_lv1:              
                    plt.savefig(config.root + config.results + day +  "/" + config.small_total_var + str(custid))
                elif (performance_metric < config.decisive_TV_lv2) and \
                    (performance_metric > config.decisive_TV_lv1):
                    plt.savefig(config.root + config.results + day +  "/" + config.big_total_var + str(custid))
            else:
                if performance_metric > config.decisive_MaSS_lv1:
                    plt.savefig(config.root + config.results + day +  "/" + config.more_than_one_cluster_good + str(custid))
                elif (performance_metric > config.decisive_MaSS_lv2) and \
                    (performance_metric < config.decisive_MaSS_lv1):
                    plt.savefig(config.root + config.results + day +  "/" + config.more_than_one_cluster_pretty + str(custid))
        else:             
            plt.savefig(config.root + config.results + day +  "/" + str(custid))
        plt.close()
    
    @staticmethod
    def get_CSV_format_data(custid, day, data, best_combination, is_single_pattern, performance_metric, config, 
                            quickly_test_running = 0, easy_to_see = 1):
        # ========================================= get verified data =========================================
        desired_cols = ["matchid", "bettype", "liveindicator", "transdate", "sporttype"]
        if isinstance(best_combination, str):
            best_combination = [int(x) for x in best_combination.split(",") if x != ""]
            verified_data = data[data.transid.isin(best_combination)][desired_cols]
        else:
            # print("best_combination = %s" % best_combination)
            (matchid, bettypeid, is_live) = best_combination
            verified_data = data[(data.matchid == matchid) & (data.bettype == bettypeid) 
                                & (data.liveindicator == is_live) & (data.custid == custid)][desired_cols]
        # ========================================= assign verified data into appropriate location =========================================
        if config.is_detected_by_new_method:
            if easy_to_see:
                verified_data.to_csv(config.root + config.results + day +  "/"  + config.easy_to_see + str(custid) + ".csv", index = False)
            else:
                verified_data.to_csv(config.root + config.results + day +  "/"  + config.hard_to_see + str(custid) + ".csv", index = False)
        else:
            if quickly_test_running:
                verified_data.to_csv(config.root + config.results + day +  "/"  + config.quickly_test + str(custid) + ".csv", index = False)
            else:
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