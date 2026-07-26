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

    def _inspect(self):
        return self._run_pip("inspect")

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

        req = self._generate_temp_requirements()
        _args.extend(("-r", req.name))

        _result = self._install(*_args)

        req.close()
        os.remove(req.name)

        return _result

    def uninstall(self, *packages: str):
        return self._uninstall(*packages)

    def list(self) -> dict[str, str]:
        _logs = self._list("--format", "json")
        _packages = json.loads("".join(_logs))

        return {_p["name"]: _p["version"] for _p in _packages}

    def update(self, *args):
        _args = [*args]

        req = self._generate_temp_requirements()
        _args.extend(("-r", req.name))

        _result = self._update(*_args)

        req.close()
        os.remove(req.name)

        return _result

    def self_update(self):
        return self.update("pip")

    def dry_install(self):
        _results = {}

        req = self._generate_temp_requirements()

        with NamedTemporaryFile("w+", suffix=".json", delete=False, encoding="utf-8") as f:
            self._install("--dry-run", "-r", req.name, "--report", f.name, "-U")
            f.seek(0)
            _data = json.load(f)

        req.close()
        f.close()

        os.remove(req.name)
        os.remove(f.name)

        return _data

    def get_info(self, *packages: str) -> dict[str, PackageInfo]:
        _logs = self._inspect()
        _all_packages = json.loads("\n".join(_logs))["installed"]

        _results = {}
        _data = {}

        for _p in _all_packages:
            _name = _p["metadata"]["name"]
            _version = _p["metadata"].get("version", "0.0.0")
            _summary = _p["metadata"].get("summary", "No summary available")
            _data[_name] = {
                "name": _name,
                "version": _version,
                "summary": _summary
            }

        for package in packages:
            _results[package] = PackageInfo.model_validate(_data[package])

        return _results
