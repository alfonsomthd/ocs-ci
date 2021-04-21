import logging
import pytest
import time
import random

from ocs_ci.framework.testlib import ManageTest, tier2, skipif_ocs_version, bugzilla
from ocs_ci.ocs.resources.pod import get_ceph_tools_pod, get_osd_pods, get_osd_pod_id

log = logging.getLogger(__name__)


@tier2
@bugzilla("1938049")
@skipif_ocs_version("<4.7")
@pytest.mark.polarion_id("OCS-2512")
class TestOSDHeapProfile(ManageTest):
    """
    Test osd heap profile created on '/var/log/ceph/'.

    """

    def test_osd_heap_profile(self):
        """
        1.Start heap profiler for osd
          $ oc exec rook-ceph-tools-85ccf9f7c5-v7bgk ceph tell osd.0 heap start_profiler

        2.Dump heap profile
          $ oc exec rook-ceph-tools-85ccf9f7c5-v7bgk ceph tell osd.0 heap dump

        3.Get heap profile in /var/log/ceph dir on osd node
          $ oc rsh rook-ceph-osd-0-959dbdc6d-pddd4
            sh-4.4# ls -ltr /var/log/ceph/
            -rw-r--r--. 1 ceph ceph 295891 Apr 11 14:33 osd.0.profile.0001.heap

        """
        strings_err = ["error", "fail"]
        osd_pods = get_osd_pods()
        osd_id = str(random.randint(0, len(osd_pods) - 1))

        log.info(f"Start heap profiler for osd-{osd_id}")
        pod_tool = get_ceph_tools_pod()
        out = pod_tool.exec_sh_cmd_on_pod(
            command=f"ceph tell osd.{osd_id} heap start_profiler"
        )
        logging.info(out)
        for string_err in strings_err:
            if string_err in out.lower():
                raise (ValueError, f"{out}")

        time.sleep(10)

        log.info("Dump heap profile")
        out = pod_tool.exec_sh_cmd_on_pod(command=f"ceph tell osd.{osd_id} heap dump")
        logging.info(out)
        for string_err in strings_err:
            if string_err in out.lower():
                raise (ValueError, f"{out}")

        log.info(f"Get osd-{osd_id} pod object")
        for osd_pod in osd_pods:
            if get_osd_pod_id(osd_pod) == osd_id:
                osd_pod_profile = osd_pod

        log.info(f"Verify osd.{osd_id}.profile log exist on /var/log/ceph/")
        out = osd_pod_profile.exec_cmd_on_pod(command="ls -ltr /var/log/ceph/")
        log.info(out)
        if f"osd.{osd_id}.profile" not in out:
            raise Exception(
                f"osd.{osd_id}.profile log does not exist on /var/log/ceph/\n{out}"
            )
