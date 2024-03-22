import os
import shutil
import requests
import tarfile
from .utils import *

def download(version):
    if(not os.path.exists(os.path.os.getcwd() + "/dolibarr_archives/" + version + "/" + version + '.tar.gz')):
        os.makedirs(os.path.os.getcwd() + "/dolibarr_archives/" + version , 511, True)
        url = 'https://github.com/Dolibarr/dolibarr/archive/refs/tags/' + version + '.tar.gz'
        file_to_save = os.path.os.getcwd() + "/dolibarr_archives/" + version + "/" + version + '.tar.gz'
        resp = requests.get(url)
        with open(file_to_save, "wb") as f: 
            f.write(resp.content)

def setup(user, version, name):
    tar = tarfile.open(os.path.os.getcwd() + "/dolibarr_archives/" + version + "/" + version + '.tar.gz', "r:gz")
    tar.extractall(os.path.os.getcwd() + "/Users/" + user + "/sources/")
    shutil.rmtree(os.path.os.getcwd() + "/Users/" + user + "/sources/" + name,True)
    os.rename(os.path.os.getcwd() + "/Users/" + user + "/sources/" + "dolibarr-" + version, os.path.os.getcwd() + "/Users/" + user + "/sources/" + name)
    tar.close()

    #chargement des fichiers nécessaires à l'installation d'un dolibarr (conf, fichier permettant d'installer automatiquement)
    os.makedirs(os.path.os.getcwd() + "/Users/" + user + "/environment/dolibarr", 511, True)
    shutil.rmtree(os.path.os.getcwd() + "/Users/" + user + "/environment/dolibarr")
    shutil.copytree(os.path.os.getcwd() + "/static_files/dolibarr", os.path.os.getcwd() + "/Users/" + user + "/environment/dolibarr")
    
    replaceInFiles(os.path.os.getcwd() + "/Users/" + user + "/environment/dolibarr/conf/",{'${USER}':user,'${DOLIBARR_NAME}':name})
    replaceInFiles(os.path.os.getcwd() + "/Users/" + user + "/environment/dolibarr/install/",{'${USER}':user,'${DOLIBARR_NAME}':name})

    shutil.copyfile(os.path.os.getcwd() + "/Users/" + user + "/environment/dolibarr" + "/conf/conf.php", os.path.os.getcwd() + "/Users/" + user + "/sources/"+name+"/htdocs/conf/conf.php")
    shutil.copyfile(os.path.os.getcwd() + "/Users/" + user + "/environment/dolibarr" + "/install/autoinstall.php", os.path.os.getcwd() + "/Users/" + user + "/sources/"+name+"/htdocs/install/autoinstall.php")    
    #todo installforced
    
    return 1 