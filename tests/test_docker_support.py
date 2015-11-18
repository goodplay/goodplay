# -*- coding: utf-8 -*-

import pytest

from goodplay.docker_support import DockerRunner


@pytest.fixture
def without_docker_env_vars(monkeypatch):
    monkeypatch.delenv('DOCKER_TLS_VERIFY', raising=False)
    monkeypatch.delenv('DOCKER_HOST', raising=False)
    monkeypatch.delenv('DOCKER_CERT_PATH', raising=False)
    monkeypatch.delenv('DOCKER_MACHINE_NAME', raising=False)


def test_client_negotiates_version(without_docker_env_vars, mocker):
    client_mock = mocker.patch('docker.Client', autospec=True)

    docker_runner = DockerRunner(ctx=None)
    docker_runner.client

    client_mock.assert_called_once_with(version='auto')


def test_client_uses_docker_host_env_var(without_docker_env_vars, monkeypatch, mocker):
    monkeypatch.setenv('DOCKER_HOST', 'tcp://192.168.10.2:2376')

    client_mock = mocker.patch('docker.Client', autospec=True)

    docker_runner = DockerRunner(ctx=None)
    docker_runner.client

    _, _, kwargs = client_mock.mock_calls[0]
    assert kwargs['base_url'] == 'tcp://192.168.10.2:2376'


def test_client_does_not_validate_hostname(without_docker_env_vars, mocker):
    mocker.patch('docker.Client', autospec=True)
    kwargs_from_env_mock = mocker.patch('docker.utils.kwargs_from_env', autospec=True)

    docker_runner = DockerRunner(ctx=None)
    docker_runner.client

    kwargs_from_env_mock.assert_called_once_with(assert_hostname=False)


def test_client_is_cached(mocker):
    client_mock = mocker.patch('docker.Client', autospec=True)

    docker_runner = DockerRunner(ctx=None)
    first_result = docker_runner.client

    assert id(docker_runner.client) == id(first_result)
    assert client_mock.call_count == 1
