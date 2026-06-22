from rlgym_learn_venv_manager.api.virtual_environment import (
    VenvConfig,
    VirtualEnvironment,
)

if __name__ == "__main__":
    _venv_config = VenvConfig(
        python_executable="rlgym-learn-venv\\.venv\\Scripts\\python.exe"
    )
    _venv = VirtualEnvironment()
    _venv.load(_venv_config)

    _venv.delete()
