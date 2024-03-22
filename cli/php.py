import typer
import docker
import getpass
from envparts.php import Php
app = typer.Typer()

client = docker.from_env() 
@app.command()
def install(version: str):
    print(f"Installation de PHP version {version}")
    php = Php(client,getpass.getuser())
    php.set_version(version)
    print(f"Création des fichiers nécessaires au service")
    php.setup_files()
    print(f"Construction du service ... ")
    php.build()
    print(f"Lancement du service ... ")
    php.run()
    print("Ok !")

if __name__ == "__main__":
    app()
