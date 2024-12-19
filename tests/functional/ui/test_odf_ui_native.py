import logging
import os
import pytest
import subprocess

from ocs_ci.utility.utils import get_kubeadmin_password
from ocs_ci.ocs.ocp import get_ocp_url


logger = logging.getLogger(__name__)


def run_cmd(cmd, cwd, env):
    return subprocess.run(
        cmd, capture_output=True, check=True, cwd=cwd, env=env, text=True
    )


@pytest.mark.odf_ui_native_e2e()
def test_ui():
    """
    Launch ODF console native E2E tests.
    """
    env = os.environ.copy()
    env["BRIDGE_KUBEADMIN_PASSWORD"] = get_kubeadmin_password()
    env["BRIDGE_BASE_ADDRESS"] = get_ocp_url()

    data_dir = "./data"
    odf_console_dir = f"{data_dir}/odf-console"
    # Consider using quay.io/ocs-dev/odf-console-ci-runner:node20 image to launch e2e tests.
    try:
        if not os.path.exists(odf_console_dir):
            run_cmd(
                [
                    "git",
                    "clone",
                    "--depth=1",
                    "git@github.com:red-hat-storage/odf-console.git",
                ],
                cwd=data_dir,
                env=env,
            )
        if not os.path.exists(f"{odf_console_dir}/node_modules/.bin/cypress"):
            run_cmd(["yarn", "install"], cwd=odf_console_dir, env=env)
        run_cmd(
            [
                "yarn",
                "test-cypress-headless",
                "--spec",
                "cypress/tests/list-page.spec.ts",
            ],
            cwd=odf_console_dir,
            env=env,
        )
    except subprocess.CalledProcessError as e:
        logger.exception("ERROR.")
        raise e
