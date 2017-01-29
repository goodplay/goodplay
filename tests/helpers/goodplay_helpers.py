# -*- coding: utf-8 -*-

from __future__ import print_function

import io
import tarfile
import textwrap

import docker
import pytest
import requests


def is_docker_available():
    docker_client = docker.from_env()

    try:
        docker_client.version(api_version=False)
        return True
    except requests.exceptions.ConnectionError:
        return False


skip_if_no_docker = pytest.mark.skipif(
    not is_docker_available(),
    reason='docker is not available')


def smart_create(base_path, smart_content):
    smart_content = textwrap.dedent(smart_content)

    print(smart_content)

    for rel_path, content in smart_content_iter(smart_content, path_prefix='## '):
        path = base_path.join(*rel_path.split('/'))

        if path.basename.endswith('.tar.gz'):
            path.dirpath().ensure(dir=True)

            with tarfile.open(str(path), 'w:gz') as tar:
                for rel_tar_path, tar_content in smart_content_iter(content, path_prefix='#### '):
                    tar_bytes_content = tar_content.encode('utf-8')
                    info = tarfile.TarInfo(rel_tar_path)
                    info.size = len(tar_bytes_content)
                    tar.addfile(info, io.BytesIO(tar_bytes_content))
        else:
            path.write(content, ensure=True)


def smart_content_iter(smart_content, path_prefix):
    rel_path = None
    content = []

    for line in smart_content.splitlines():
        if line.startswith(path_prefix):
            if rel_path:
                yield rel_path, '\n'.join(content)
            rel_path = line[len(path_prefix):]
            content = []
        else:
            content.append(line)

    if rel_path:
        yield rel_path, '\n'.join(content)
