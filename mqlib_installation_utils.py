import sys
import logging
import subprocess
import shutil
from tempfile import TemporaryDirectory
from pathlib import Path

logger = logging.getLogger(__name__)

MQLIB_PATH = Path.home() / ".mqlib_bin"
MQLIB_EXEC_PATH = MQLIB_PATH / "MQLib"
REPO_URL = "https://github.com/LuchnikovI/MQLib"


def uninstall_mqlib() -> None:
    if MQLIB_PATH.exists():
        shutil.rmtree(MQLIB_PATH)
    logger.info("MQLib executable has been uninstalled")


def create_mqlib_dir() -> None:
    MQLIB_PATH.mkdir(parents=True, exist_ok=True)


def check_tool_exists(tool: str) -> None:
    if shutil.which(tool) is None:
        raise RuntimeError(f"{tool} is not installed or not in PATH")


def install_mqlib() -> None:
    create_mqlib_dir()
    with TemporaryDirectory() as build:
        check_tool_exists("git")
        check_tool_exists("make")
        build_path = Path(build)
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", "master", REPO_URL, str(build_path)],
            check=True,
        )
        subprocess.run(
            ["make"],
            cwd=build_path,
            check=True,
        )
        shutil.copy2(build_path / "bin" / "MQLib", MQLIB_EXEC_PATH)
        MQLIB_EXEC_PATH.chmod(
            MQLIB_EXEC_PATH.stat().st_mode | 0o111
        )
        logger.info("MQLib executable has been installed")


def ensure_mqlib() -> None:
    if MQLIB_EXEC_PATH.exists():
        logger.info("MQLib executable is found")
    else:
        logger.info(f"MQLib executable has not been found, it will be instaled in {MQLIB_PATH}")
        try:
            install_mqlib()
        except BaseException:
            logger.exception(f"MQLib instalation failed, {MQLIB_PATH} will be uninstalled")
            uninstall_mqlib()
            sys.exit(1)

