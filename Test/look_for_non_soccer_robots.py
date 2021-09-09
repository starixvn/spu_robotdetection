import os
import pandas as pd
from tqdm import tqdm

def check_user_eligible_for_some_condition(data):
    # num_bettype =  data.bettype.nunique()
    num_match =  data.matchid.nunique()
    # if num_match == data.shape[0] and num_match > 30:
    if num_match == 1 and data.shape[0] > 20:
        return True
    else:
        # sport_type = data.sporttype.unique()[0]
        # if sport_type == 1:
        #     return False
        # else:
        #     return True
        return False

def walk_through_all_users(parent_folder, child_folder, mode):
    cases = os.listdir(parent_folder + child_folder + "/" + mode + "/")
    # cases = cases[:1]
    for case in cases:
        data = pd.read_csv(parent_folder + child_folder + "/" + mode + "/" + case)
        # print(data.sporttype.unique()[0])
        if check_user_eligible_for_some_condition(data):
            custid = case.split(".")[0]
            print("\nchild_folder = %s --- %s --- custid = %s\n" % (child_folder, mode, custid))

parent_folder = "D:/Project/Robot Detection/RESULTSV3/"

children_folders = sorted(os.listdir(parent_folder))
# print("children_folders = " + str(children_folders))
# children_folders = children_folders[:1]
for child_folder in tqdm(children_folders, desc = "Checking . . ."):
    walk_through_all_users(parent_folder, child_folder, mode = "Easy_To_See")
    walk_through_all_users(parent_folder, child_folder, mode = "Hard_To_See")