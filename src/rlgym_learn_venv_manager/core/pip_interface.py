import json
import os
from tempfile import NamedTemporaryFile

from rlgym_learn_venv_manager.core.process import is_interpreter_valid, run_subprocess
from rlgym_learn_venv_manager.core.return_data import PackageInfo

INDIVIDUAL_SHOW_PACKAGE_OUTPUT_LEN = 11


class PIPInterface:
    def __init__(self, interpreter: str | os.PathLike[str]) -> None:
        self.interpreter = interpreter

    def is_interpreter_valid(self) -> bool:
        return is_interpreter_valid(self.interpreter)

    def run_with_interpreter(self, *args) -> list[str]:
        if not self.is_interpreter_valid():
            raise ValueError(f"Interpreter {self.interpreter} is invalid.")

        return run_subprocess(self.interpreter, "-X", "-utf8", *args)

    def _run_pip(self, *args):
        return self.run_with_interpreter("-m", "pip", *args)

    def _install(self, *args):
        return self._run_pip("install", *args)

    def _update(self, *args):
        return self._install("-U", *args)

    def _uninstall(self, *args):
        return self._run_pip("uninstall", "-y", *args)

    def _list(self, *args):
        return self._run_pip("list", *args)

    def _show(self, *args):
        return self._run_pip("show", *args)

    def _generate_temp_requirements(self):
        req = NamedTemporaryFile("r+", suffix=".txt", delete=False)
        _packages = self.list()
        req.write("\n".join(_packages.keys()))
        req.seek(0)

        return req

    # ---- public methods

    def install(
        self,
        package: str | None = None,
        requirements: str | os.PathLike[str] | None = None,
        *args,
    ):
        if package is None and requirements is None:
            raise ValueError(
                "Must have at least a package or a requirements file to install"
            )

        _args = [*args]

        if package is not None:
            _args.append(package)
        if requirements is not None:
            _args.extend(("-r", requirements))

        return self._install(*_args)

    def uninstall(self, *packages: str):
        return self._uninstall(*packages)

    def list(self) -> dict[str, str]:
        _logs = self._list("--format", "json")
        _packages = json.loads("".join(_logs))

        return {_p["name"]: _p["version"] for _p in _packages}

    def update(self, *args):
        return self._update(*args)

    def self_update(self):
        return self.update("pip")

    def dry_install(self):
        _results = {}

        req = self._generate_temp_requirements()

        with NamedTemporaryFile("w+", suffix=".json", delete=False) as f:
            self._install("--dry-run", "-r", req.name, "--report", f.name, "-U")
            f.seek(0)
            _data = json.load(f)

        req.close()
        f.close()

        os.remove(req.name)
        os.remove(f.name)

        return _data

    def get_info(self, *packages: str) -> dict[str, PackageInfo]:
        _logs = self._show(*packages)

        _results = {}

        for i in range(len(packages)):
            _name_l, _version_l, _summary_l = _logs[
                i * INDIVIDUAL_SHOW_PACKAGE_OUTPUT_LEN : i
                * INDIVIDUAL_SHOW_PACKAGE_OUTPUT_LEN
                + 3
            ]
            _name = _name_l.split(" ")[1]
            _version = _version_l.split(" ")[1]
            _summary = " ".join(_summary_l.split(" ")[1:])

            _results[_name] = PackageInfo(
                name=_name, version=_version, summary=_summary
            )

        return _results
