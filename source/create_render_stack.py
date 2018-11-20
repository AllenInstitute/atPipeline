import os

def main():
    f = open("MyTest.out", 'w')

    statetablefile="/data/scripts/statetable_ribbon_4_session_1_section_0"
    project="MyProject"
    owner="test"
    session=1
    projectroot="/data/M335503_Ai139_smallvol/raw/data/Ribbon0004/session01"

    #upload acquisition stacks
    dcmd = "docker exec renderapps python -m renderapps.dataimport.create_fast_stacks "
    dcmd = dcmd + "--render.host localhost "
    dcmd = dcmd + "--render.client_scripts /var/www/render/render-ws-java-client/src/main/scripts "
    dcmd = dcmd + "--render.port 80 "
    dcmd = dcmd + "--render.memGB 5G "
    dcmd = dcmd + "--log_level INFO "
    dcmd = dcmd + "--statetableFile %s "%statetablefile
    dcmd = dcmd + "--render.project %s "%project
    dcmd = dcmd + "--projectDirectory %s "%projectroot
    dcmd = dcmd + "--outputStackPrefix ACQ_S0%d"%(session)
    dcmd = dcmd + " --render.owner %s "%owner
    f.write(dcmd + "\n")
    os.system(dcmd)
    f.close()
    exit(0)


if __name__ == '__main__':
    main()
