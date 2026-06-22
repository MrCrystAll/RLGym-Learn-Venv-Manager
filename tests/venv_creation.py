import sys

from rlgym_learn_venv_manager.api.factory import (
    VenvFactoryConfig,
    VirtualEnvironmentFactory,
)

if __name__ == "__main__":
    _venv_factory_config = VenvFactoryConfig(
        path_to_project="rlgym-learn-venv",
        python_base_executable=sys.executable,
        base_requirements=["rlgym-learn", "rlgym[rl]"],
    )

    _venv_factory = VirtualEnvironmentFactory()
    _venv_factory.load(_venv_factory_config)
    _venv = _venv_factory.create()
