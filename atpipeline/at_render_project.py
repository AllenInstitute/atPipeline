

class RenderProject:
    def __init__(self, owner, project_name, host_name, host_port, client_scripts, mem_gb, log_level):
        self.owner          = owner
        self.projectName    = project_name
        self.host           = host_name
        self.hostPort       = host_port
        self.clientScripts  = client_scripts
        self.memGB          = mem_gb
        self.logLevel       = log_level