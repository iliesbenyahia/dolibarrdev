import os
import shutil 
from .utils import replaceInFiles


class Apache:

    def __init__(self, dockerClient, owner, network = "traefik"):
        self.dockerClient = dockerClient
        self.owner = owner
        self.image = self.owner + "-apache"
        self.container = self.owner + "-apache"
        self.network = "traefik"
        self.target_dir = os.path.os.getcwd() + "/Users/" + self.owner + "/environment/apache" 

    def setup_files(self):
        if os.path.exists(self.target_dir):
            shutil.rmtree(self.target_dir)
        shutil.copytree(os.path.os.getcwd() + "/static_files/environment/apache", self.target_dir)
        replaceInFiles(self.target_dir,{'${USER}':self.owner})

    def build(self):
        if(self.dockerClient.images.list(self.image)):
            self.dockerClient.images.remove(image=self.image)
        self.dockerClient.images.build(path=self.target_dir,tag=self.image,rm=True)

    def run(self):
        if(not self.dockerClient.containers.list(False, None,{"name":self.container})):
            self.dockerClient.containers.run(
                self.image, 
                detach=True,
                name=self.container, 
                network=self.network,
                volumes = {os.path.os.getcwd() + "/Users/" + self.owner + "/sources": {'bind': '/var/www/html', 'mode': 'rw'}},
                          labels = {
                              "traefik.http.routers."+self.owner+"-apache.rule" : "Host(`"+self.owner+".docker.localhost`)",
                              "traefik.http.services."+self.owner+"-apache.loadbalancer.server.port" : "80",
                              "owner" : self.owner
                              })
        
    
