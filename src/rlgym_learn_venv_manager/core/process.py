import os
import subprocess


def run_subprocess(*args) -> list[str]:
    _logs = []
    _errs = []

    _process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONUTF8": "1"},
    )

    for _line in _process.stdout:
        _logs.append(_line.decode(errors="replace").strip())

    for _line in _process.stderr:
        _errs.append(_line.decode(errors="replace").strip())

    _success = _process.wait() == 0

    if not _success:
        _full_error = "\n".join(_errs)
        raise ValueError(_full_error)

    return _logs


def is_interpreter_valid(interpreter: str | os.PathLike[str]) -> bool:
    _exists_check = os.path.exists(interpreter)
    _name_check = str(interpreter).endswith("python.exe")

    if not _exists_check or not _name_check:
        return False

    run_subprocess(interpreter, "-c", "x = 1")

    return _exists_check and _name_check
