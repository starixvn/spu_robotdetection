import json
# import datetime
class CTS_DC_RobotDetection_InsertDAModel(object):
    def __init__(self,*args):
        self.ip_RobotInfo: json = args[0]
        # self.ip_ScanDate: datetime = args[1]
        self.op_ErrorMessage = None
        
    def __call__(self):
        return [self.ip_RobotInfo, self.op_ErrorMessage]
