import configparser
import os


class Configuration(object):
    """description of class"""
    def __init__(self, *args, **kwargs):
        path = os.path.dirname(__file__)
        config = configparser.ConfigParser()
        config.read(os.path.join(path, args[0]))
        self.config = config
        self.ENV = args[1]

        # define paths
        self.root = self.getDataStrConfig(
            self.config, 'DEFAULT', 'ROOT')
        self.save_dir_log = self.getDataStrConfig(
            self.config, 'DEFAULT', 'SAVE_DIR_LOG')
        self.log_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'LOG_NAME')
        self.results = self.getDataStrConfig(
            self.config, 'DEFAULT', 'results')
        self.small_total_var = self.getDataStrConfig(
            self.config, 'DEFAULT', 'small_total_var')
        self.big_total_var = self.getDataStrConfig(
            self.config, 'DEFAULT', 'big_total_var')
        self.no_cluster = self.getDataStrConfig(
            self.config, 'DEFAULT', 'no_cluster')
        self.more_than_one_cluster_pretty = self.getDataStrConfig(
            self.config, 'DEFAULT', 'more_than_one_cluster_pretty')
        self.more_than_one_cluster_good = self.getDataStrConfig(
            self.config, 'DEFAULT', 'more_than_one_cluster_good')
        self.data_path = self.getDataStrConfig(
            self.config, 'DEFAULT', 'data_path')
        # self.backup = self.getDataStrConfig(self.config, 'DEFAULT', 'BACK_UP')
        self.quickly_test = self.getDataStrConfig(
            self.config, 'DEFAULT', 'quickly_test')
        self.easy_to_see = self.getDataStrConfig(
            self.config, 'DEFAULT', 'easy_to_see')
        self.hard_to_see = self.getDataStrConfig(
            self.config, 'DEFAULT', 'hard_to_see')
        self.app_name = self.getDataStrConfig(self.config, 'DEFAULT', 'APP_NAME')

        # define GroupBetting config
        self.decisive_MaSS_lv1 = float(self.getDataStrConfig(
            self.config, 'ROBOT_DETECTION_CONFIG', 'decisive_MaSS_lv1'))
        self.decisive_MaSS_lv2 = float(self.getDataStrConfig(
            self.config, 'ROBOT_DETECTION_CONFIG', 'decisive_MaSS_lv2'))
        self.min_samples = int(self.getDataStrConfig(
            self.config, 'ROBOT_DETECTION_CONFIG', 'min_samples'))
        self.num_outstanding = int(self.getDataStrConfig(
            self.config, 'ROBOT_DETECTION_CONFIG', 'num_outstanding'))
        self.window_size = int(self.getDataStrConfig(
            self.config, 'ROBOT_DETECTION_CONFIG', 'window_size'))
        # self.strtime_format = self.getDataStrConfig(
        #     self.config, 'ROBOT_DETECTION_CONFIG', 'strtime_format')
        self.decisive_TV_lv2 = float(self.getDataStrConfig(
            self.config, 'ROBOT_DETECTION_CONFIG', 'decisive_TV_lv2'))
        self.decisive_TV_lv1 = float(self.getDataStrConfig(
            self.config, 'ROBOT_DETECTION_CONFIG', 'decisive_TV_lv1'))
        self.ratio_criteria = int(self.getDataStrConfig(
            self.config, 'ROBOT_DETECTION_CONFIG', 'ratio_criteria'))
        self.quickly_test_by_MBL = int(self.getDataStrConfig(
            self.config, 'ROBOT_DETECTION_CONFIG', 'quickly_test_by_MBL'))
        self.is_clustered_by_MBL = int(self.getDataStrConfig(
            self.config, 'ROBOT_DETECTION_CONFIG', 'is_clustered_by_MBL'))
        self.is_save_all_in_one = int(self.getDataStrConfig(
            self.config, 'ROBOT_DETECTION_CONFIG', 'is_save_all_in_one'))
        self.is_detected_by_new_method = int(self.getDataStrConfig(
            self.config, 'ROBOT_DETECTION_CONFIG', 'is_detected_by_new_method'))
        self.minimum_suspicious_transID = int(self.getDataStrConfig(
            self.config, 'ROBOT_DETECTION_CONFIG', 'minimum_suspicious_transID'))
        self.is_assigned_to_PeriodRange = int(self.getDataStrConfig(
            self.config, 'ROBOT_DETECTION_CONFIG', 'is_assigned_to_PeriodRange'))
        
        # define information db SPU
        self.aimluser = self.getDataStrConfig(
            self.config, 'SPU_AIML_DB', 'USERNAME')
        self.aimlpwd = self.getDataStrConfig(
            self.config, 'SPU_AIML_DB', 'PASSWORD')
        self.aimlhost = self.getDataStrConfig(
            self.config, 'SPU_AIML_DB', 'HOST')
        self.aimlport = self.getDataStrConfig(
            self.config, 'SPU_AIML_DB', 'PORT')
        self.aimldb = self.getDataStrConfig(
            self.config, 'SPU_AIML_DB', 'DATABASE_NAME')

        # define information db CTS
        self.ctsuser = self.getDataStrConfig(
            self.config, 'CTS_DataCenter_DB', 'USERNAME')
        self.ctspwd = self.getDataStrConfig(
            self.config, 'CTS_DataCenter_DB', 'PASSWORD')
        self.ctshost = self.getDataStrConfig(
            self.config, 'CTS_DataCenter_DB', 'HOST')
        self.ctsport = self.getDataStrConfig(
            self.config, 'CTS_DataCenter_DB', 'PORT')
        self.ctsdb = self.getDataStrConfig(
            self.config, 'CTS_DataCenter_DB', 'DATABASE_NAME')

        # define is transfer data to CTS
        self.chunk_size = int(self.getDataStrConfig(
            self.config, 'ACTION_DB', 'chunk_size'))
        self.insert_to_aiml = self.getDataBooleanConfig(
            self.config, 'ACTION_DB', 'insert_to_aiml')


    @classmethod
    def getDataStrConfig(self, config, parent, child):
        config.sections()
        return config[parent][child]

    @classmethod
    def getDataBooleanConfig(self, config, parent, child):
        config.sections()
        return config[parent].getboolean(child)
    
ENV = 'LOCAL'
if ENV == 'LOCAL':
    config = Configuration("localconfig.ini", ENV)
else:
    config = Configuration("proconfig.ini", ENV)


