#-------------------------------------------------------------------------------
# Name:        at_SPARK
# Purpose:
#-------------------------------------------------------------------------------

#Simple class that estimate spark parameters
class Spark:
    def __init__(self, hostMemory, hostCores, dataInfo):
        self.host_memory    = hostMemory
        self.host_cores     = hostCores
        self.data_info      = dataInfo


        self.default_parallelism = 8
        self.driver_memory       = "10g"
        self.executor_memory     = "10g"
        self.executor_cores      = 10






