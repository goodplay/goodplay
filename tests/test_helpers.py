# -*- coding: utf-8 -*-

import tarfile

from goodplay_helpers import smart_create


def test_smart_create_empty(tmpdir):
    smart_create(tmpdir, '')

    assert tmpdir.listdir() == []


def test_smart_create_linebreaks_before_first_file(tmpdir):
    smart_create(tmpdir, '''

    ## file1
    Hello World
    ''')

    assert tmpdir.join('file1').check(file=True)
    assert tmpdir.join('file1').read() == 'Hello World'


def test_smart_create_single_file_empty(tmpdir):
    smart_create(tmpdir, '''
    ## file1

    ''')

    assert tmpdir.join('file1').check(file=True)
    assert tmpdir.join('file1').read() == ''


def test_smart_create_single_file_single_line(tmpdir):
    smart_create(tmpdir, '''
    ## file1
    Hello World
    ''')

    assert tmpdir.join('file1').check(file=True)
    assert tmpdir.join('file1').read() == 'Hello World'


def test_smart_create_single_file_multiple_lines(tmpdir):
    smart_create(tmpdir, '''
    ## file1
    Hello
    World
    ''')

    assert tmpdir.join('file1').check(file=True)
    assert tmpdir.join('file1').read() == 'Hello\nWorld'


def test_smart_create_single_file_in_subdir(tmpdir):
    smart_create(tmpdir, '''
    ## dir1/file1
    Hello
    World
    ''')

    assert tmpdir.join('dir1').check(dir=True)
    assert tmpdir.join('dir1', 'file1').check(file=True)
    assert tmpdir.join('dir1', 'file1').read() == 'Hello\nWorld'


def test_smart_create_multiple_files(tmpdir):
    smart_create(tmpdir, '''
    ## file1
    Hello
    World
    ## file2
    Hello, John Doe
    ''')

    assert tmpdir.join('file1').check(file=True)
    assert tmpdir.join('file1').read() == 'Hello\nWorld'

    assert tmpdir.join('file2').check(file=True)
    assert tmpdir.join('file2').read() == 'Hello, John Doe'


def test_smart_create_complex(tmpdir):
    smart_create(tmpdir, '''
    ## VERSION
    1.0.1

    ## docs/README.md
    # My project

    ## helloworld/main.py
    print 'Hello World'

    ''')

    assert tmpdir.join('VERSION').read() == '1.0.1\n'
    assert tmpdir.join('docs', 'README.md').read() == '# My project\n'
    assert tmpdir.join('helloworld', 'main.py').read() == "print 'Hello World'\n"


def test_smart_create_single_archive_single_file(tmpdir):
    smart_create(tmpdir, '''
    ## archive.tar.gz
    #### file1
    Hello World
    ''')

    archive_path = tmpdir.join('archive.tar.gz')
    extracted_path = tmpdir.join('archive.tar.gz.extracted')
    extracted_path.ensure(dir=True)

    with tarfile.open(str(archive_path), 'r:gz') as tar:
        tar.extractall(str(extracted_path))

    assert extracted_path.join('file1').read() == 'Hello World'


def test_smart_create_single_archive_multiple_files(tmpdir):
    smart_create(tmpdir, '''
    ## archive.tar.gz
    #### file1
    Hello World
    #### file2
    Hello
    World
    ''')

    archive_path = tmpdir.join('archive.tar.gz')
    extracted_path = tmpdir.join('archive.tar.gz.extracted')
    extracted_path.ensure(dir=True)

    with tarfile.open(str(archive_path), 'r:gz') as tar:
        tar.extractall(str(extracted_path))

    assert extracted_path.join('file1').read() == 'Hello World'
    assert extracted_path.join('file2').read() == 'Hello\nWorld'


def test_smart_create_single_archive_in_subdir(tmpdir):
    smart_create(tmpdir, '''
    ## dir1/archive.tar.gz
    #### file1
    Hello World
    ''')

    assert tmpdir.join('dir1').check(dir=True)

    archive_path = tmpdir.join('dir1', 'archive.tar.gz')
    extracted_path = tmpdir.join('archive.tar.gz.extracted')
    extracted_path.ensure(dir=True)

    with tarfile.open(str(archive_path), 'r:gz') as tar:
        tar.extractall(str(extracted_path))

    assert extracted_path.join('file1').read() == 'Hello World'


def test_smart_create_single_archive_with_subdirs(tmpdir):
    smart_create(tmpdir, '''
    ## archive.tar.gz
    #### dir1/dir2/hello_world.py
    print 'Hello World'
    #### another/README
    Some text
    ''')

    archive_path = tmpdir.join('archive.tar.gz')
    extracted_path = tmpdir.join('archive.tar.gz.extracted')
    extracted_path.ensure(dir=True)

    with tarfile.open(str(archive_path), 'r:gz') as tar:
        tar.extractall(str(extracted_path))

    assert extracted_path.join('dir1', 'dir2', 'hello_world.py').read() == "print 'Hello World'"
    assert extracted_path.join('another', 'README').read() == 'Some text'


def test_smart_create_multiple_archives_multiple_files(tmpdir):
    smart_create(tmpdir, '''
    ## archive1.tar.gz
    #### file1
    Hello World
    ## archive2.tar.gz
    #### file2
    Content of file2
    ''')

    # extract archive1.tar.gz
    archive1_path = tmpdir.join('archive1.tar.gz')
    extracted1_path = tmpdir.join('archive1.tar.gz.extracted')
    extracted1_path.ensure(dir=True)

    with tarfile.open(str(archive1_path), 'r:gz') as tar:
        tar.extractall(str(extracted1_path))

    assert extracted1_path.join('file1').read() == 'Hello World'

    # extract archive2.tar.gz
    archive2_path = tmpdir.join('archive2.tar.gz')
    extracted2_path = tmpdir.join('archive2.tar.gz.extracted')
    extracted2_path.ensure(dir=True)

    with tarfile.open(str(archive2_path), 'r:gz') as tar:
        tar.extractall(str(extracted2_path))

    assert extracted2_path.join('file2').read() == 'Content of file2'
