import json
import datetime
class SPU_InsertRobotUsersDAModel(object):
    def __init__(self,*args):
        self.ip_RobotInfo: json = args[0]
        self.ip_ScanDate: datetime = args[1]
        self.op_ErrorMessage = None
        
    def __call__(self):
        return [self.ip_RobotInfo, self.ip_ScanDate, self.op_ErrorMessage]
