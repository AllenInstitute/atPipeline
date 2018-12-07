import docker

try:
    client = docker.from_env()
    print (client.containers.list())
    #make state table
    projectroot = "/nas/data/M33"
    project =  "M33"
    statetablefile = "/nas/data/M33/statetables/test"
    ribbon = 4
    session = 1
    sectnum = 1
    owner="bla"


    cmd = "python /pipeline/make_state_table_ext_multi_pseudoz.py "
    cmd = cmd + "--projectDirectory %s "%projectroot
    cmd = cmd + "--outputFile  %s "%statetablefile
    cmd = cmd + "--oneribbononly True "
    cmd = cmd + "--ribbon %d "%ribbon
    cmd = cmd + "--session %d "%session
    cmd = cmd + "--section %d "%sectnum

    print ("Running command: " + cmd)
    #container = client.containers.run("render-p-apps:latest", cmd, detach=True)
    container = client.containers.get("d3443e6df9")
    #test = container.exec_run(cmd)
    #print(test)


    dcmd = "python -m renderapps.dataimport.create_fast_stacks "
    dcmd = dcmd + "--render.host localhost "
    dcmd = dcmd + "--render.client_scripts /var/www/render/render-ws-java-client/src/main/scripts "
    dcmd = dcmd + "--render.port 8080 "
    dcmd = dcmd + "--render.memGB 5G "
    dcmd = dcmd + "--log_level INFO "
    dcmd = dcmd + "--statetableFile %s "%statetablefile
    dcmd = dcmd + "--render.project %s "%project
    dcmd = dcmd + "--projectDirectory %s "%projectroot
    dcmd = dcmd + "--outputStackPrefix ACQ_S0%d"%(session)
    dcmd = dcmd + " --render.owner %s "%owner
    print (dcmd)
######            f.write(dcmd + "\n")
    test = container.exec_run(dcmd)
    print(test)


    print("No exception occured..")
except Exception as e:
    print(e)


