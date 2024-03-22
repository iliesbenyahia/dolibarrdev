import typer
from typing_extensions import Annotated

app = typer.Typer()


@app.command()
def start(
        rebuild: Annotated):
    print("Démarrage de l'environnement")

@app.command()
def create(name: str, version: str):
    print(f"Création de votre dolibarr \"{name}\" en version {version}")

@app.command()
def delete(name: str):
    print(f"Suppression de votre dolibarr {name}")


@app.command()
def list():
    print(f"Liste des dolibarrs")


if __name__ == "__main__":
    app()
