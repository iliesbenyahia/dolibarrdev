import os
import docker
import shutil
import requests
import tarfile
from services.apache import Apache

client = docker.from_env() 

def getDolibarrArchive(version):
    if(not os.path.exists(os.path.os.getcwd() + "/dolibarr_archives/" + version + "/" + version + '.tar.gz')):
        os.makedirs(os.path.os.getcwd() + "/dolibarr_archives/" + version , 511, True)
        url = 'https://github.com/Dolibarr/dolibarr/archive/refs/tags/' + version + '.tar.gz'
        file_to_save = os.path.os.getcwd() + "/dolibarr_archives/" + version + "/" + version + '.tar.gz'
        resp = requests.get(url)
        with open(file_to_save, "wb") as f: 
            f.write(resp.content) 
    return 1

def getDolibarr(username, version, name):
    getDolibarrArchive(version)
    tar = tarfile.open(os.path.os.getcwd() + "/dolibarr_archives/" + version + "/" + version + '.tar.gz', "r:gz")
    tar.extractall(os.path.os.getcwd() + "/Users/" + username + "/sources/")
    os.rename(os.path.os.getcwd() + "/Users/" + username + "/sources/" + "dolibarr-" + version, os.path.os.getcwd() + "/Users/" + username + "/sources/" + name)
    tar.close()
    os.makedirs(os.path.os.getcwd() + "/Users/" + username + "/setup_files/dolibarr")
    shutil.copytree(os.path.os.getcwd() + "/static_files/dolibarr", os.path.os.getcwd() + "/Users/" + username + "/setup_files/dolibarr")
    replaceInFiles(os.path.os.getcwd() + "/Users/" + username + "/setup_files/dolibarr",'${USER}',username)
    replaceInFiles(os.path.os.getcwd() + "/Users/" + username + "/setup_files/dolibarr",'${DOLIBARR_NAME}',name) #optimiser la fonction ou utiliser l'autre ? faudrait faire des tests voir laquelle est la plus rapide :)
    
    shutil.copyfile(os.path.os.getcwd() + "/Users/" + username + "/setup_files/dolibarr" + "/conf/conf.php", os.path.os.getcwd() + "/Users/" + username + "/sources/"+name+"/htdocs/conf/conf.php")
    shutil.copyfile(os.path.os.getcwd() + "/Users/" + username + "/setup_files/dolibarr" + "/autoinstall.php", os.path.os.getcwd() + "/Users/" + username + "/sources/"+name+"/htdocs/install.forced.php")
    #shutil.copyfile(os.path.os.getcwd() + "/Users/" + username + "/setup_files/dolibarr" + "/install/autoinstall.php", os.path.os.getcwd() + "/Users/" + username + "/sources/"+name+"/htdocs/conf/conf.php")
    
    
    return 1 



def scan_dir(root_dir, search_text, replace_text):
    if os.path.exists(root_dir) and os.path.isdir(root_dir):
        for dirs, name, files in os.walk(root_dir, topdown=True, followlinks=False):
            for file in files:
                content = None
                if not file.startswith('.'):
                    current_item = os.path.join(dirs, file)
                with open(current_item, 'r') as f:
                    content = f.read()
                    content = content.replace(search_text, replace_text)

                with open(current_item, 'w') as b_file:
                    b_file.write(content)
    else:
        return
    
def replaceInFiles(root_dir, search_text, replace_text):
    with os.scandir(root_dir) as it:
    # Iterate over directory entries
        for entry in it:
            # If not file continue to next iteration
            # This is no need if you are 100% sure there is only files in the directory
            if not entry.is_file():
                continue

            # Read the file
            with open(entry.path, 'r') as file:
                filedata = file.read()

            # Replace the target string
            filedata = filedata.replace(search_text, replace_text)

            # write the file out again
            with open(entry.path, 'w') as file:
                file.write(filedata)
    
def runTraefik():
    containerName = 'traefik'
    networkName = 'traefik'
    if(not client.networks.list(names=containerName)):
        client.networks.create(networkName)
    if(not client.containers.list(False, None,{"name":containerName})):
        client.containers.run('traefik:v2.10',
                          detach=True,
                          name=containerName,
                          ports={
                              '8080/tcp':8080,
                              '80/tcp':80 
                          },
                          network=networkName, 
                          volumes=[os.path.os.getcwd() + '/config_files/traefik/traefik.yml:/etc/traefik/traefik.yml', 
                                   '/var/run/docker.sock:/var/run/docker.sock'],
                        
                          
                          )
    
def prepareUserEnv(username):
    os.makedirs(os.path.os.getcwd() + "/Users/" + username + "/sources/", 511, True) #droits à revoir ?
    os.makedirs(os.path.os.getcwd() + "/Users/" + username + "/custom/", 511, True) #droits à revoir ? 


def setupUserApache2(username, **kwargs):
    imageName = username + "-apache"
    containerName = username + "-apache"
    networkName = "traefik"

    options = {
        'rebuild' : True
    }

    options.update(**kwargs)
    os.makedirs(os.path.os.getcwd() + "/Users/" + username + "/sources/custom", 511, True)
    
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    shutil.copytree(os.path.os.getcwd() + "/static_files/environment/apache", target_dir)
    replaceInFiles(target_dir,'${USER}',username)
    if(client.images.list(imageName)):
        client.images.remove(image=imageName)
    client.images.build(path=target_dir,tag=imageName, 
                          rm=True)
    if(not client.containers.list(False, None,{"name":containerName})):
        container = client.containers.run(imageName, 
                          detach=True,
                          name=containerName, 
                          network=networkName,
                          volumes = {os.path.os.getcwd() + "/Users/" + username + "/sources": {'bind': '/var/www/html', 'mode': 'rw'}},
                          labels = {
                              "traefik.http.routers."+username+"-apache.rule" : "Host(`"+username+".docker.localhost`)",
                              "traefik.http.services."+username+"-apache.loadbalancer.server.port" : "80"
                              })

    #traefiknetwork = client.networks.list(names="traefik")[0]
    #traefiknetwork.connect(container = apacheContainer)

def setupUserApache(username):
    apache = Apache(client,username)
    apache.setup_files()
    apache.build()
    apache.run()
    

#todo : enlever les conteneur intermédiaire
def setUserPhp(username, version="8.1", **kwargs):
    imageName = username + "-php"
    containerName = username + "-php"
    networkName = "traefik"

    options = {
        'rebuild' : True
    }

    options.update(**kwargs)

    os.makedirs(os.path.os.getcwd() + "/Users/" + username + "/sources/custom", 511, True)
    target_dir = os.path.os.getcwd() + "/Users/" + username + "/environment/php" 
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    shutil.copytree(os.path.os.getcwd() + "/static_files/environment/php", target_dir)
    replaceInFiles(target_dir,'${PHP_VERSION}',version)
    if(client.images.list(imageName)):
        client.images.remove(image=imageName)
    client.images.build(path=target_dir,tag=imageName,
                          rm=True)
    if(not client.containers.list(False, None,{"name":containerName})):
        container = client.containers.run(imageName, 
                          detach=True, 
                          name=containerName, 
                          network="traefik",
                          volumes = {os.path.os.getcwd() + "/Users/" + username + "/sources": {'bind': '/var/www/html', 'mode': 'rw'}}
                          #labels = {
                             # "traefik.http.routers."+username+"-apache.rule" : "Host(`"+username+".docker.localhost`)",
                            # "traefik.http.services."+username+"-apache.loadbalancer.server.port" : "80"
                            #  }
    )
        

def setUserMariaDB(username, version ='latest'):
    imageName = "mariadb-"+version
    containerName = username + "-db"
    networkName = "traefik"

    os.makedirs(os.path.os.getcwd() + "/Users/" + username + "/database", 511, True)

    if(not client.images.list(name=imageName)):
        client.images.pull(imageName)
    if(not client.containers.list(False, None,{"name":containerName})):
        container = client.containers.run(imageName, 
                          detach=True,
                          name=containerName, 
                          network=networkName,
                          #volumes = {os.path.os.getcwd() + "/Users/" + username + "/sources": {'bind': '/var/www/html', 'mode': 'rw'}},
                          labels = {
                              "traefik.http.services."+username+"-db.loadbalancer.server.port" : "3306"
                              })
    return 1