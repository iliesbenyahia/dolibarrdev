import getpass
import typer
from envparts import dolibarr
from rich import print

app = typer.Typer()


@app.command()
def install(name: str, version: str):
    print("Télechargement de Dolibarr")
    dolibarr.download(version)
    print("Installation dans le répertoire utilisateur")
    dolibarr.setup(getpass.getuser(), version, name)
    


if __name__ == "__main__":
    app()
