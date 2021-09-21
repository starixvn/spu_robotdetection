# import json
import datetime
class SPU_AIML_RD_ComputeRobotUsersDAModel(object):
    def __init__(self,*args):
        # self.ip_RobotInfo: json = args[0]
        self.ip_ScanDate: datetime = args[0]
        self.op_ErrorMessage = None
        
    def __call__(self):
        return [self.ip_ScanDate, self.op_ErrorMessage]
