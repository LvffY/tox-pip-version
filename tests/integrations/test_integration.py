from os import path
from subprocess import check_call
from tempfile import TemporaryDirectory

import pytest

"""Integration tests for our tox plugin"""

HERE = path.realpath(path.dirname(__file__))
PACKAGE_DIR = path.realpath(path.join(HERE, "../.."))


def setup_fresh_venv(tag):
    temp_dir = TemporaryDirectory(prefix=tag)
    venv_dir = path.join(temp_dir.name, "venv")
    check_call(["virtualenv", venv_dir])
    print(f"Created venv: {venv_dir}")
    return temp_dir, venv_dir


def install_deps(venv_dir, *deps):
    """Install a dependency into the virtualenv"""
    pip = path.join(venv_dir, "bin", "pip")
    cmd = [pip, "install"] + list(deps)
    check_call(cmd, cwd=venv_dir, env={})


def _run_case(venv_dir, subdirectory, env=None):
    tox_work_dir = path.join(venv_dir, ".tox")
    directory = path.join(HERE, subdirectory)
    activate = path.join(venv_dir, "bin", "activate")
    command = f". {activate}; pip freeze; tox --workdir {tox_work_dir}"
    print(f"Running: '{command}'")
    check_call(command, cwd=directory, shell=True, env=env)


# List test cases (which match tests sub-directory) and possibly add some environment variables
CASES = [
    ("test-two-envs", {}),
    ("test-env-inheritance", {}),
    ("test-environment-variable", {"TOX_SETUPTOOLS_VERSION": "58.0.0"}),
    ("test-version-specifiers", {}),
]


@pytest.mark.parametrize("subdirectory,env", CASES)
def test_with_tox_version(subdirectory, env):
    """
    Tests our plugin outside of all other plugin and/or other framework.

    :param subdirectory: Test case to run
    :return:
    """
    temp_dir, venv_dir = setup_fresh_venv(tag=subdirectory)
    try:
        install_deps(venv_dir, "tox")
        install_deps(venv_dir, PACKAGE_DIR)
        _run_case(venv_dir, subdirectory, env=env)
    finally:
        temp_dir.cleanup()


# Add one case when using tox_pip_version
AIRFLOW_CASES = CASES + [
    (
        "test-with-airflow",
        {
            "TOX_SETUPTOOLS_VERSION": "58.0.0",
            "TOX_PIP_VERSION": "20.2.4",
        },
    )
]


@pytest.mark.parametrize("subdirectory,env", AIRFLOW_CASES)
def test_with_tox_version_with_tox_pip_version(subdirectory, env):
    """
    Test our plugin when using in combination with tox-pip-version.

    At the very first version it didn't work very well because of some bad interaction issues (because we were implementing the same tox hook)

    This tests are able to install airflow (which was the root cause of this plugin)
    :param case: test case to run
    :return: Nothin, just run the tests
    """
    env["TOX_PIP_VERSION"] = "20.2.4"

    temp_dir, venv_dir = setup_fresh_venv(tag=subdirectory)
    try:
        install_deps(venv_dir, "tox", "tox-pip-version")
        install_deps(venv_dir, PACKAGE_DIR)
        _run_case(venv_dir, subdirectory, env=env)
    finally:
        temp_dir.cleanup()
