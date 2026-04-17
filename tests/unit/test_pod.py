import pytest

from storectl.domain.models.pod import Pod, PodStatus


class TestPodStatus:
    def test_has_running(self) -> None:
        assert PodStatus.RUNNING is not None

    def test_has_pending(self) -> None:
        assert PodStatus.PENDING is not None

    def test_has_failed(self) -> None:
        assert PodStatus.FAILED is not None

    def test_has_unknown(self) -> None:
        assert PodStatus.UNKNOWN is not None

    def test_has_succeeded(self) -> None:
        assert PodStatus.SUCCEEDED is not None


class TestPod:
    def test_creation(self) -> None:
        pod = Pod(
            name="pod-1",
            namespace="default",
            status=PodStatus.RUNNING,
            node_name="node-1",
            restart_count=0,
        )
        assert pod.name == "pod-1"
        assert pod.namespace == "default"
        assert pod.status == PodStatus.RUNNING
        assert pod.node_name == "node-1"
        assert pod.restart_count == 0

    def test_name_cannot_be_empty(self) -> None:
        with pytest.raises(ValueError):
            Pod(
                name="",
                namespace="default",
                status=PodStatus.RUNNING,
                node_name="node-1",
                restart_count=0,
            )

    def test_namespace_cannot_be_empty(self) -> None:
        with pytest.raises(ValueError):
            Pod(
                name="pod-1",
                namespace="",
                status=PodStatus.RUNNING,
                node_name="node-1",
                restart_count=0,
            )

    def test_restart_count_cannot_be_negative(self) -> None:
        with pytest.raises(ValueError):
            Pod(
                name="pod-1",
                namespace="default",
                status=PodStatus.RUNNING,
                node_name="node-1",
                restart_count=-1,
            )

    def test_is_running(self) -> None:
        pod = Pod(
            name="pod-1",
            namespace="default",
            status=PodStatus.RUNNING,
            node_name="node-1",
            restart_count=0,
        )
        assert pod.is_running() is True

    def test_is_not_running(self) -> None:
        pod = Pod(
            name="pod-1",
            namespace="default",
            status=PodStatus.FAILED,
            node_name="node-1",
            restart_count=0,
        )
        assert pod.is_running() is False

    def test_is_healthy_no_restarts(self) -> None:
        pod = Pod(
            name="pod-1",
            namespace="default",
            status=PodStatus.RUNNING,
            node_name="node-1",
            restart_count=0,
        )
        assert pod.is_healthy() is True

    def test_is_unhealthy_too_many_restarts(self) -> None:
        pod = Pod(
            name="pod-1",
            namespace="default",
            status=PodStatus.RUNNING,
            node_name="node-1",
            restart_count=5,
        )
        assert pod.is_healthy() is False
