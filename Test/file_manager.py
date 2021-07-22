import os
import pandas as pd
from tqdm import tqdm
if __name__=="__main__":
    location = "D:/Project/Robot Detection/data/data_month6/"
    saving_location = "D:/Project/Robot Detection/data/daily_in_June/"
    prefix = "bettrans_06_"
    suffix = "_2021_"
    # myStr_check = "bettrans_06_01_2021_00_3"
    # target_cus = 1086772
    days = [str(z).zfill(2) for z in range(1, 31)]
    list_files = os.listdir(location)
    for day in days:
        data = pd.concat([pd.read_csv(location + fn, skipfooter = 1, skiprows = [1]) 
                        for fn in tqdm(list_files) if fn.startswith(prefix + day + suffix)])
        # print("HEAD of data\n", data.head())
        # print("TAIL of data\n", data.tail())
        # targeted_data = data[data.custid == target_cus]
        data.to_csv(saving_location + "2021-06-" + day  + ".csv", index = False)
    # targeted_data.to_csv(saving_location + str(target_cus) + ".csv", index = False)
    # try:
    #     results_path = "D:/Project/Robot Detection/RESULTS/"
    #     day = "2021-06-01"
    #     os.makedirs(results_path + day)
    # except FileExistsError:
    #     print("diego")
    #     pass