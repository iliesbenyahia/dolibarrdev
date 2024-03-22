class Service:
    def __init__(self, dockerClient, owner, network = "traefik"):
        self.dockerClient = dockerClient
        self.owner = owner
        self.image = self.owner + "-apache"
        self.container = self.owner + "-apache"
        self.network = "traefik"

    def setup_files(self):
        pass

    async def build(self):
        if(self.dockerClient.images.list(self.image)):
            self.dockerClient.images.remove(image=self.image)
        self.dockerClient.images.build(path=self.target_dir,tag=self.image,rm=True)

    def run(self):
        pass
    
