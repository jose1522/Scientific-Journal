from app import app  # Imports the "app" object from __init__.py, located in the app folder.

if __name__ == "__main__":
    app.run()  # runs the flask app through "Lazy loading" (not through a real server)