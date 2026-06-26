import os
import shutil

from pydantic import BaseModel

from rlgym_learn_venv_manager.core.pip_interface import PIPInterface


class VenvConfig(BaseModel):
    python_executable: str | os.PathLike[str]


class VirtualEnvironment:
    def load(self, config: VenvConfig):
        self.config = config
        self.pip = PIPInterface(config.python_executable)

    # Install

    def install_package(self, package: str, *args):
        return self.pip.install(package=package, *args)

    def install_requirements(self, requirements: str | os.PathLike[str], *args):
        return self.pip.install(requirements=requirements, *args)

    # Update

    def update(self, *args):
        return self.pip.update(*args)

    def get_all_update_status(self) -> dict[str, str]:
        _results = {}

        _dry_run_report = self.pip.dry_install()
        _installs = _dry_run_report["install"]

        for _install in _installs:
            _metadata = _install["metadata"]
            _results[_metadata["name"]] = _metadata["version"]

        return _results

    def get_all_packages(self):
        return self.pip.list()

    def delete(self):
        shutil.rmtree(
            os.path.join(self.config.python_executable, "..", "..")
        )  # Delete the whole tree ".venv/<dir>/<dir>"

    def uninstall(self, package: str):
        return self.pip.uninstall(package)
