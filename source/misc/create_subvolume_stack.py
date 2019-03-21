import os
import timeit
import subprocess
##example_parameters={
##    "render":{
##        "host":"ibs-forrestc-ux1",
##        "port":80,
##        "owner":"S3_Run1",
##        "project":"S3_Run1_Rosie",
##        "client_scripts":"/var/www/render/render-ws-java-client/src/main/scripts"
##    },
##    'input_stack':'Rough_Aligned_140_to_141_DAPI_1',
##    'output_stack':'Subvolume_Rough_Aligned_140_to_141_DAPI_1',
##    'directory' : '/nas2/data/S3_Run1_Rosie/processed/subvolume',
##    'minX':-1500,
##    'maxX':-500,
##    'minY':-5700,
##    'maxY':-4700,
##    'minZ':0,
##    'maxZ':25,
##    'pool_size':5
##
##}


def run():
    input_stack  = "STI_Session1"
    output_stack = "SV_STI_Session1"
    owner        = "ATExplorer"
    project      = "M33"
    minZ         = 400
    maxZ         = 404
    minX         = 1500
    maxX         = 2500
    minY         = 5700
    maxY         = 6700
    pool_size    = 5

    #upload acquisition stacks
    cmd = "docker exec renderapps_multchan python -m renderapps.stack.create_subvolume_stack"
    cmd = cmd + " --render.host W10DTMJ03EG6Z.corp.alleninstitute.org"
    cmd = cmd + " --render.client_scripts /shared/render/render-ws-java-client/src/main/scripts"
    cmd = cmd + " --render.port 80"
    cmd = cmd + " --render.memGB 5G"
    cmd = cmd + " --render.owner %s "%owner
    cmd = cmd + " --render.project %s "%project
    cmd = cmd + " --log_level INFO"
    cmd = cmd + " --directory %s "%("/mnt/data/M33/processed/subvolume")
    cmd = cmd + " --input_stack %s"%input_stack
    cmd = cmd + " --output_stack %s"%output_stack
    cmd = cmd + " --minX %d"%minX
    cmd = cmd + " --maxX %d"%maxX
    cmd = cmd + " --minY %d"%minY
    cmd = cmd + " --maxY %d"%maxY
    cmd = cmd + " --minZ %d"%minZ
    cmd = cmd + " --maxZ %d"%maxZ
    cmd = cmd + " --pool_size %d"%pool_size

    #Run =============
    logger.info("Running: " + cmd.replace('--', '\n--'))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    for line in proc.stdout.readlines():
        logger.info(line.rstrip())

if __name__ == '__main__':
    timeStart = timeit.default_timer()
    run()

    timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
    logger.info("Elapsed time: " + timeDuration + " minutes")