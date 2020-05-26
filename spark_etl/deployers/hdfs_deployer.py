import uuid
import subprocess
import os

from .abstract_deployer import AbstractDeployer
from spark_etl import Build

def _execute(host, cmd, error_ok=False):
    r = subprocess.call(["ssh", "-q", "-t", host, cmd], shell=False)
    if not error_ok and r != 0:
        raise Exception(f"command {cmd} failed with exit code {r}")


class HDFSDeployer(AbstractDeployer):
    """
    This deployer deploys application to HDFS
    """
    def __init__(self, config):
        super(HDFSDeployer, self).__init__(config)

    def deploy(self, build_dir, deployment_location):
        # let's copy files to the stage dir
        bridge_dir = os.path.join(self.config['stage_dir'], str(uuid.uuid4()))

        bridge = self.config["bridge"]
        _execute(bridge, f"mkdir -p {bridge_dir}")

        build = Build(build_dir)

        for artifact in build.artifacts:
            subprocess.call([
                'scp', '-q', f"{build_dir}/{artifact}", f"{bridge}:{bridge_dir}/{artifact}"
            ])

        dest_location = f"{deployment_location}/{build.version}"
        _execute(bridge, f"hdfs dfs -rm -r {dest_location}", error_ok=True)
        _execute(bridge, f"hdfs dfs -mkdir -p {dest_location}")
        for artifact in build.artifacts:
            _execute(bridge, f"hdfs dfs -copyFromLocal {bridge_dir}/{artifact} {dest_location}/{artifact}")
        _execute(bridge, f"rm -rf {bridge_dir}")