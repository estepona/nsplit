import os

import pytest

from src.app import split_, merge_


@pytest.mark.parametrize(
    'dirpath, src, dst, chunk',
    [
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/dup.mov',
            '/mnt/c/Users/estep/Videos/Captures/dup_copy.mov',
            5,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/mgs1.mp4',
            '/mnt/c/Users/estep/Videos/Captures/mgs1_copy.mp4',
            5,
        ),
    ],
)
def test_size(dirpath, src, dst, chunk):
  split_(src, chunk, '')
  merge_(dirpath, True)

  srcfile_size = os.stat(src).st_size
  dstfile_size = os.stat(dst).st_size

  assert srcfile_size == dstfile_size
