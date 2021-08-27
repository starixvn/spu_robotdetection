import pandas as pd
import numpy as np
from tqdm import tqdm
import sys
sys.path.append("C:/Users/diego.nguyen/diegoProj/Follow_darius/robotdetection/")
from Robot_Detection_Manager.Robot_Detection_Manager import Robot_Detection_Manager
file_path = "D:/Project/Robot Detection/data/robot_users_detected_by_New_Method_with_Period_Chain.csv"

data = pd.read_csv(file_path)

dates = np.sort(data.CreatedDate.unique())
total_yankees = 0
# for date in tqdm(dates, desc = "Convert Period Chain to Period Range"):
for date in dates:
    json_List = []
    sub_data = data[data.CreatedDate == date]
    milisecond_distance = sub_data[sub_data.PeriodChain.isna()]
    num_yankees = len(milisecond_distance)
    if num_yankees > 0:
        total_yankees += num_yankees
        print("\nDay %s has %s yankees" % (date, num_yankees))
        # special_list = milisecond_distance.CustID.unique()
        milisecond_distance = milisecond_distance[["CustID", "TransIDSequence"]]
        milisecond_distance["TransIDSequence"] = ""
        milisecond_distance = milisecond_distance.to_dict(orient = "records")
        for cus_data in milisecond_distance:
            custID = cus_data["CustID"]
            super_dangerous_tickets = cus_data["TransIDSequence"]
            if super_dangerous_tickets == "":
                super_dangerous_tickets = 77
            else:
                super_dangerous_tickets = super_dangerous_tickets.split(",")
                super_dangerous_tickets = len(super_dangerous_tickets) // 2
            new_cus_dict = {"C":int(custID), "M":"", "B":"", "LI":"", "ISP":"", "DM":"", "TS":"",
                            "PR0":super_dangerous_tickets, 
                            "PR1":0, 
                            "PR2":0, 
                            "PR3":0, 
                            "PR4":0, 
                            "PR5":0, 
                            "PR6":0, 
                            "PR7":0, 
                            "PR8":0, 
                            "PR9":0, 
                            "PR10":0}
            json_List.append(new_cus_dict)
        print("json_List %s yankees" % len(json_List))
    periodic_distance = sub_data[~ sub_data.PeriodChain.isna()]
    periodic_distance = periodic_distance[["CustID", "PeriodChain"]]
    periodic_distance = periodic_distance.to_dict(orient = "records")
    for cus_data in periodic_distance:
        custID = cus_data["CustID"]
        new_cus_dict = {"C":int(custID), "M":"", "B":"", "LI":"", "ISP":"", "DM":"", "TS":"",
                        "PR0":0, 
                        "PR1":0, 
                        "PR2":0, 
                        "PR3":0, 
                        "PR4":0, 
                        "PR5":0, 
                        "PR6":0, 
                        "PR7":0, 
                        "PR8":0, 
                        "PR9":0, 
                        "PR10":0}
        PeriodChain = cus_data["PeriodChain"]
        PeriodChain = PeriodChain.split(",")
        PeriodChain = [float(x) for x in PeriodChain]
        for element in PeriodChain:
            order_of_range = int(element // 5) + 1
            if order_of_range > 10:
                order_of_range = 10
            new_cus_dict["PR" + str(order_of_range)] += 1
        json_List.append(new_cus_dict)
    Robot_Detection_Manager.insert_robot_user_to_DB(json_List, date)
print("\nTotal Yankess = " + str(total_yankees))
