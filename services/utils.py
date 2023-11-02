import os
import shutil
import requests

def replaceInFiles(root_dir, replacements):
    with os.scandir(root_dir) as it:
        for entry in it:
            if not entry.is_file():
                continue

            with open(entry.path, 'r') as file:
                filedata = file.read()

            for search_text, replace_text in replacements.items():
                filedata = filedata.replace(search_text, replace_text)

            with open(entry.path, 'w') as file:
                file.write(filedata)

def downladDolibarr(version):
    if(not os.path.exists(os.path.os.getcwd() + "/dolibarr_archives/" + version + "/" + version + '.tar.gz')):
        os.makedirs(os.path.os.getcwd() + "/dolibarr_archives/" + version , 511, True)
        url = 'https://github.com/Dolibarr/dolibarr/archive/refs/tags/' + version + '.tar.gz'
        file_to_save = os.path.os.getcwd() + "/dolibarr_archives/" + version + "/" + version + '.tar.gz'
        resp = requests.get(url)
        with open(file_to_save, "wb") as f: 
            f.write(resp.content) 
    return 1

def setupDolibarr(username, version, name):
    downladDolibarr(version)
    tar = tarfile.open(os.path.os.getcwd() + "/dolibarr_archives/" + version + "/" + version + '.tar.gz', "r:gz")
    tar.extractall(os.path.os.getcwd() + "/Users/" + username + "/sources/")
    os.rename(os.path.os.getcwd() + "/Users/" + username + "/sources/" + "dolibarr-" + version, os.path.os.getcwd() + "/Users/" + username + "/sources/" + name)
    tar.close()
    os.makedirs(os.path.os.getcwd() + "/Users/" + username + "/setup_files/dolibarr")
    shutil.copytree(os.path.os.getcwd() + "/static_files/dolibarr", os.path.os.getcwd() + "/Users/" + username + "/setup_files/dolibarr")
    replaceInFiles(os.path.os.getcwd() + "/Users/" + username + "/setup_files/dolibarr",{'${USER}':username,'${DOLIBARR_NAME}':name})
    shutil.copyfile(os.path.os.getcwd() + "/Users/" + username + "/setup_files/dolibarr" + "/conf/conf.php", os.path.os.getcwd() + "/Users/" + username + "/sources/"+name+"/htdocs/conf/conf.php")
    shutil.copyfile(os.path.os.getcwd() + "/Users/" + username + "/setup_files/dolibarr" + "/autoinstall.php", os.path.os.getcwd() + "/Users/" + username + "/sources/"+name+"/htdocs/install.forced.php")    
    return 1 