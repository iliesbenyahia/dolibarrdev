import typer
import getpass
import docker
from envparts.apache import Apache
from rich import print

app = typer.Typer()
client = docker.from_env() 

@app.command()
def install():
    print("Création du service Apache ...")
    apache = Apache(client,getpass.getuser())
    print("Copie des fichiers nécessaires au service ...")
    apache.setup_files()
    print("Construction de l'image Apache")
    apache.build()
    print("Lancement du service Apache ...")
    apache.run()
    print("OK !")

@app.command()
def delete(name: str):
    print(f"Suppression de votre dolibarr {name}")


@app.command()
def list():
    print(f"Liste des dolibarrs")


if __name__ == "__main__":
    app()
