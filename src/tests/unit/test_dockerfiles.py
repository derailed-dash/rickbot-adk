import os


def test_dockerfiles_exist():
    """Verify that the required Dockerfiles for the sidecar architecture exist."""
    project_root = os.getcwd()
    required_files = [
        "Dockerfile.react_fe",
        "Dockerfile.api_sidecar"
    ]
    for file_name in required_files:
        file_path = os.path.join(project_root, file_name)
        assert os.path.exists(file_path), f"{file_name} is missing from the project root."

def test_docker_compose_has_sidecar_services():
    """Verify that docker-compose.yml has the react_fe and api_sidecar services."""
    import yaml
    with open("docker-compose.yml") as f:
        compose = yaml.safe_load(f)
    services = compose.get("services", {})
    assert "react_fe" in services, "react_fe service is missing from docker-compose.yml"
    assert "api_sidecar" in services, "api_sidecar service is missing from docker-compose.yml"

def test_makefile_has_docker_react():
    """Verify that the Makefile has the docker-react target."""
    with open("Makefile") as f:
        content = f.read()
    assert "docker-react:" in content, "docker-react target is missing from Makefile"
