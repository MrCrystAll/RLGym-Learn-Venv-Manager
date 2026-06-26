import os

from rlgym_learn_venv_manager.core.process import is_interpreter_valid, run_subprocess


def get_python_version(python_interpreter: str | os.PathLike[str]) -> str:
    if not is_interpreter_valid(python_interpreter):
        raise ValueError("Interpreter is invalid. Couldn't check python version")

    _logs = run_subprocess(python_interpreter, "-V")
    return _logs[0].split(" ")[1]


def get_python_default_executables() -> list[str]:
    _command = ["where", "python"] if os.name == "nt" else ["which", "python3"]
    return run_subprocess(*_command)
