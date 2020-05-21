import os
import subprocess
import tempfile
from contextlib import contextmanager, suppress
import shutil

@contextmanager
def _act_in_dir(new_dir):
    current_dir = os.getcwd()
    try:
        os.chdir(new_dir)
        yield
    finally:
        os.chdir(current_dir)

class Application:
    """Represent a spark application
    """

    def __init__(self, location):
        """
        Parameters
        ----------
        location: str
            The location of the application
        """
        self.location = location


    def build(self, destination):
        """
        Build the application
        """

        current_dir = os.getcwd()

        os.makedirs(destination, exist_ok=True)

        tmpdir = tempfile.mkdtemp()
        subprocess.run([
            "pip", "install", "-r", f"{self.location}/requirements.txt",
            "-t", tmpdir
        ])

        # generate archive for lib
        with suppress(OSError):
            os.remove(f"{destination}/lib.zip")
        with _act_in_dir(tmpdir):
            subprocess.run([
                'zip', "-r", f"{destination}/lib.zip", "."
            ])
        shutil.rmtree(tmpdir)

        # generate archive for app
        with suppress(OSError):
            os.remove(f"{destination}/app.zip")
        with _act_in_dir(self.location):
            subprocess.run([
                'zip', "-r", f"{destination}/app.zip", "."
            ])

        shutil.copyfile(f"{self.location}/main.py", f"{destination}/main.py")
