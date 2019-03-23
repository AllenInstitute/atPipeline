#-------------------------------------------------------------------------------
# Name:        atcore
# Purpose:     atcore super class
#
# Author:      matsk
#
# Created:     Mar 22, 2019
#-------------------------------------------------------------------------------
import at_system_config as c

class ATCore:
    def __init__(self, parameters : c.ATSystemConfig):
        self.parameters = parameters

