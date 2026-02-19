import bcrypt
import typer
from database import engine
from models import AdminAuth
from sqlmodel import Session, select

app = typer.Typer()


@app.command()
def create_admin(
    username: str = typer.Option(..., prompt=True),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, confirmation_prompt=True
    ),
):
    """
    Create a new admin user for the Syntesa Attendance system using native bcrypt.
    """
    with Session(engine) as session:
        existing_user = session.exec(
            select(AdminAuth).where(AdminAuth.username == username)
        ).first()
        if existing_user:
            typer.echo(f"Error: User '{username}' already exists.")
            raise typer.Exit(code=1)

        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

        new_admin = AdminAuth(username=username, hashed_password=hashed_pw)
        session.add(new_admin)
        session.commit()
        typer.echo(f"Successfully created admin: {username}")


if __name__ == "__main__":
    app()
