from pathlib import Path
import yaml

K8S_DIR = Path(__file__).parent.parent.parent / "k8s"
NAMESPACE_FILE = K8S_DIR / "namespace.yaml"
DEPLOYMENT_FILE = K8S_DIR / "deployment.yaml"
SERVICE_FILE = K8S_DIR / "service.yaml"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


class TestNamespaceManifest:
    def test_file_exists(self) -> None:
        assert NAMESPACE_FILE.exists()

    def test_kind_is_namespace(self) -> None:
        assert load(NAMESPACE_FILE)["kind"] == "Namespace"

    def test_name_is_storectl(self) -> None:
        assert load(NAMESPACE_FILE)["metadata"]["name"] == "storectl"

    def test_has_api_version(self) -> None:
        assert "apiVersion" in load(NAMESPACE_FILE)


class TestDeploymentManifest:
    def test_file_exists(self) -> None:
        assert DEPLOYMENT_FILE.exists()

    def test_kind_is_deployment(self) -> None:
        assert load(DEPLOYMENT_FILE)["kind"] == "Deployment"

    def test_namespace_is_storectl(self) -> None:
        assert load(DEPLOYMENT_FILE)["metadata"]["namespace"] == "storectl"

    def test_has_replicas(self) -> None:
        spec = load(DEPLOYMENT_FILE)["spec"]
        assert "replicas" in spec
        assert spec["replicas"] >= 1

    def test_has_resource_limits(self) -> None:
        containers = load(DEPLOYMENT_FILE)["spec"]["template"]["spec"]["containers"]
        assert len(containers) >= 1
        resources = containers[0].get("resources", {})
        assert "limits" in resources
        assert "requests" in resources

    def test_container_name_is_storectl(self) -> None:
        containers = load(DEPLOYMENT_FILE)["spec"]["template"]["spec"]["containers"]
        assert containers[0]["name"] == "storectl"


class TestServiceManifest:
    def test_file_exists(self) -> None:
        assert SERVICE_FILE.exists()

    def test_kind_is_service(self) -> None:
        assert load(SERVICE_FILE)["kind"] == "Service"

    def test_namespace_is_storectl(self) -> None:
        assert load(SERVICE_FILE)["metadata"]["namespace"] == "storectl"

    def test_has_selector(self) -> None:
        assert "selector" in load(SERVICE_FILE)["spec"]

    def test_has_ports(self) -> None:
        ports = load(SERVICE_FILE)["spec"]["ports"]
        assert len(ports) >= 1
