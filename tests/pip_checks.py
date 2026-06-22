from rlgym_learn_venv_manager.api.virtual_environment import (
    VenvConfig,
    VirtualEnvironment,
)

if __name__ == "__main__":
    _venv_config = VenvConfig(
        python_executable="rlgym-learn-venv/.venv/Scripts/python.exe"
    )
    _venv = VirtualEnvironment()
    _venv.load(_venv_config)

    _to_update = _venv.get_all_update_status()

    if len(_to_update) > 0:
        print(f"{len(_to_update)} package(s) to update")
        _packages = [f"{k}=={v}" for k, v in _to_update.items()]
        print("Updating...")
        _venv.update(*_packages)
        print("Finished updating.")

    print("Everything is up-to-date!")
