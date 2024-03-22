import typer
import docker
import getpass
from envparts.mariadb import MariaDB
app = typer.Typer()

client = docker.from_env() 
@app.command()
def install(version: str):
    print(f"Installation de MariaDB version {version}")
    mariadb = MariaDB(client,getpass.getuser(),version)
    print(f"Création des fichiers nécessaires au service")
    mariadb.setup_files()
    print(f"Construction du service ... ")
    mariadb.build()
    print(f"Lancement du service ... ")
    mariadb.run()
    print("Ok !")

if __name__ == "__main__":
    app()
