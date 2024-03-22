import os
import shutil 
import requests
from docker import DockerClient
from dotenv import load_dotenv
from .service import Service
from .utils import replaceInFiles

load_dotenv("../default.env")

class Php(Service):
    
    def __init__(self, dockerClient: DockerClient, owner, network = "traefik"):
        self.dockerClient = dockerClient
        self.owner = owner
        self.image = self.owner + "-php"
        self.container = self.owner + "-php"
        self.network = network
        self.target_dir = os.path.os.getcwd() + "/Users/" + self.owner + "/environment/php" 

    def is_version_available(self, version):
        search_url = f"https://hub.docker.com/v2/repositories/library/php/tags/{version}/"
        return search_url
        response = requests.get(search_url)
        data = response.json()
        if response.status_code == 200:
            data = response.json()
            for tag in data.get('results', []):
                if tag.get('name', '').startswith("fpm"):
                    return data
    
    
    def set_version(self, version, check_availability = True):
        #if(not self.is_version_available(version) and check_availability):
        #    raise ValueError(f"La version PHP {version} n'est pas disponible.") 
        self.version = version
        
    def build(self):
        if(self.dockerClient.images.list(self.image)):
            self.dockerClient.images.remove(image=self.image)
        self.dockerClient.images.build(path=self.target_dir,tag=self.image,rm=True)

    def setup_files(self):
        if os.path.exists(self.target_dir):
            shutil.rmtree(self.target_dir)
        shutil.copytree(os.path.os.getcwd() + "/static_files/environment/php", self.target_dir)
        replaceInFiles(self.target_dir, {'${PHP_VERSION}':self.version if self.version else os.getenv("DEFAULT_PHP_VERSION")})

    def run(self):
        container = self.dockerClient.containers.get(self.container)
        if(container):
            container.remove(force=True)
        container = self.dockerClient.containers.run(self.image, 
                detach=True, 
                name=self.container, 
                network="traefik",
                volumes = {os.path.os.getcwd() + "/Users/" + self.owner + "/sources": {'bind': '/var/www/html', 'mode': 'rw'}}
        )
    
