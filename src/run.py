from core import *
import platform

osName = platform.system()

if __name__ == "__main__":
    app = create_app(osName, True)
    app.run()  # runs the flask core through "Lazy loading" (not through a real server)
else:
    app = create_app(osName)
