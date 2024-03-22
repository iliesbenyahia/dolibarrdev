
import typer
from cli import dolibarr, php, apache, mariadb, environment


app = typer.Typer()

app.add_typer(dolibarr.app, name="dolibarr")
app.add_typer(php.app, name="php")
app.add_typer(apache.app, name="apache")
app.add_typer(mariadb.app, name="mariadb")
app.add_typer(environment.app, name="environment")

if __name__ == "__main__":
    app()
