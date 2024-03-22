import os
import shutil 
import requests
from .service import Service
from .utils import replaceInFiles

class MariaDB(Service):
    
    def __init__(self, dockerClient, owner, version, network = "traefik"):
        self.dockerClient = dockerClient
        self.owner = owner
        self.version = version
        self.image = 'mariadb:' + version
        self.container = self.owner + "-db"
        self.network = network
        self.target_dir = os.path.os.getcwd() + "/Users/" + self.owner + "/environment/mariadb" 
        self.root_user = "root"
        self.root_password = "root"
        self.host_directory = os.path.os.getcwd() + "/Users/" + self.owner + "/db/mariadb"
        self.container_directory = '/var/lib/mysql'
        self.volumes = {self.host_directory: {"bind": self.container_directory, "mode": "rw"}}
        self.environment = {"MYSQL_ROOT_USER": self.root_user, "MYSQL_ROOT_PASSWORD": self.root_password}
    
        
    def build(self):
        print("coucou : "+self.image)
        if(self.dockerClient.images.list(self.image)):
            self.dockerClient.images.remove(image=self.image)
        self.dockerClient.images.pull(self.image)
        self.dockerClient.images.build(path=self.target_dir,tag=self.image,rm=True)

    def setup_files(self):
        if os.path.exists(self.target_dir):
            shutil.rmtree(self.target_dir)
        shutil.copytree(os.path.os.getcwd() + "/static_files/environment/mariadb", self.target_dir)
        #TODO CHECK si self.version est bien valorisé
        #dossier dans lequel on bindera les données du conteneur
        if not os.path.exists(os.path.os.getcwd() + "/Users/" + self.owner + "/db/mariadb"):
            os.makedirs(os.path.os.getcwd() + "/Users/" + self.owner + "/db/mariadb", 777, True)
        replaceInFiles(self.target_dir, {'${MARIADB_VERSION}':self.version if self.version else os.getenv("DEFAULT_MARIADB_VERSION")})

    def run(self):
        if(not self.dockerClient.containers.list(False, None,{"name":self.container})):
            container = self.dockerClient.containers.run(self.image, 
                          detach=True, 
                          name=self.container, 
                          network="traefik",
                          volumes = self.volumes,
                          environment=self.environment,
                          ports={"3306": "3306"}
                          #labels = {
                             # "traefik.http.routers."+username+"-apache.rule" : "Host(`"+username+".docker.localhost`)",
                            # "traefik.http.services."+username+"-apache.loadbalancer.server.port" : "80"
                            #  }
        )
    
