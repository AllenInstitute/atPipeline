#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      matsk
#
# Created:     07/06/2019
# Copyright:   (c) matsk 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from atpipeline import at_atcore_api
from atpipeline.render_classes import render_stack

def main():
    core = at_atcore_api.ATCoreAPI()
    print (core.get_version())

    owner   = 'slides'
    project_name = 'M335503_Ai139_smallvol'
    source_stack   = 'S1_Session1'

    bounds = [0, 1000, 0,1000, 400, 423]

    input_stack = render_stack.RenderStack(owner = owner, project_name=project_name, stack_name = source_stack)
    bounds = render_stack.RenderStackBounds(bounds)

    core.create_subvolume_stack(input_stack, bounds)

if __name__ == '__main__':
    main()
