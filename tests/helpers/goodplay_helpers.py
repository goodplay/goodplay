# -*- coding: utf-8 -*-

from __future__ import print_function

from cStringIO import StringIO
import tarfile
import textwrap


def smart_create(base_path, smart_content):
    smart_content = textwrap.dedent(smart_content)

    print(smart_content)

    for rel_path, content in smart_content_iter(smart_content, path_prefix='## '):
        path = base_path.join(*rel_path.split('/'))

        if path.basename.endswith('.tar.gz'):
            path.dirpath().ensure(dir=True)

            with tarfile.open(str(path), 'w:gz') as tar:
                for rel_tar_path, tar_content in smart_content_iter(content, path_prefix='#### '):
                    info = tarfile.TarInfo(rel_tar_path)
                    info.size = len(tar_content)
                    tar.addfile(info, StringIO(tar_content))
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
