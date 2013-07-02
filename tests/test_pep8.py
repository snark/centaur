from nose.plugins.attrib import attr

import subprocess
import os.path
import logging
import six

TEST_DIR = os.path.dirname(__file__)
SOURCES_DIR = TEST_DIR + "/../centaur"


@attr('pep8')
class TestPep8():
    output = False
    popen = subprocess.Popen(
        ('pep8', SOURCES_DIR, TEST_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    (stdout, stderr) = popen.communicate()
    if six.PY3:
        stdoutStr = str(stdout, encoding='utf8')
    else:
        stdoutStr = stdout
    if stdoutStr != "":
        lines = stdoutStr.split("\n")
        for line in lines:
            if line != "":
                logging.error(line)
                output = True
    assert not output, "pep8 generated output"
