import os
from os.path import abspath
from tempfile import NamedTemporaryFile

from pydantic import BaseModel, Field

from rlgym_learn_venv_manager.api.virtual_environment import (
    VenvConfig,
    VirtualEnvironment,
)
from rlgym_learn_venv_manager.core.process import run_subprocess


class VenvFactoryConfig(BaseModel):
    path_to_project: str | os.PathLike[str]
    python_base_executable: str | os.PathLike[str]
    base_requirements: list[str] = Field(default_factory=list)


class VirtualEnvironmentFactory:
    def load(self, config: VenvFactoryConfig):
        self.config = config

    def _generate_venv_config(self):
        return VenvConfig(
            python_executable=os.path.join(
                self.config.path_to_project,
                ".venv",
                "bin" if os.name == "posix" else "Scripts",
                "python" + ("" if os.name == "posix" else ".exe"),
            )
        )

    def create(self) -> VirtualEnvironment:
        if os.path.exists(os.path.join(self.config.path_to_project, ".venv")):
            raise ValueError(
                f"A virtual environment already exists for project located at path {abspath(self.config.path_to_project)}"
            )

        run_subprocess(
            self.config.python_base_executable,
            "-m",
            "venv",
            os.path.join(self.config.path_to_project, ".venv"),
        )

        _venv = VirtualEnvironment()
        _config = self._generate_venv_config()
        _venv.load(_config)

        _venv.pip.self_update()  # Self update pip to get latest version

        self.install_requirements(_venv)

        return _venv

    def install_requirements(self, _venv: VirtualEnvironment):
        req = NamedTemporaryFile("r+", suffix=".txt", delete=False)
        req.write("\n".join(self.config.base_requirements))
        req.seek(0)

        _venv.install_requirements(req.name)

        req.close()
        os.remove(req.name)
