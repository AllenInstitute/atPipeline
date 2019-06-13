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

        #Default parallelism could be calculated so that
        #the (# of tile pairs) / default_parallelism = k; where k is on the order 20-100 (according to FC)
        #default_parallelism corresponds to the number of jobs executed, per core
        self.default_parallelism = 2 * hostCores

        #The driver memory can be set to half of the system memory
        self.driver_memory       = hostMemory / 2.0

        #The driver memory can be set to half of the system memory, and increased if the job fails
        self.executor_memory     = hostMemory / 2.0

        #According to Gayathri and FC, executor_cores is some default constant, k. k == 4 according to FC
        self.executor_cores      = 4






