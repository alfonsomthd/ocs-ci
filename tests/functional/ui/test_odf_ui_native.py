import logging
import os
import pytest
import subprocess

from ocs_ci.utility.utils import get_kubeadmin_password
from ocs_ci.ocs.ocp import get_ocp_url


logger = logging.getLogger(__name__)


def run_cmd(cmd, cwd, env):
    return subprocess.run(
        cmd,
        check=True,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


@pytest.mark.odf_ui_native_e2e()
def test_odf_ui():
    """
    Launch ODF console native E2E tests.
    """
    env = os.environ.copy()
    env["BRIDGE_KUBEADMIN_PASSWORD"] = get_kubeadmin_password()
    env["BRIDGE_BASE_ADDRESS"] = get_ocp_url()

    data_dir = "./data"
    try:
        run_cmd(["./run-native.sh"], cwd=data_dir, env=env)
    except subprocess.CalledProcessError as e:
        logger.error(f"\nError output:\n{e.stdout}")
        raise
