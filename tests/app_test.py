import os

import pytest

from src.app import BYTES_PER_MB, SPLITTED_PARTS_PATTERN, read_in_chunks, get_path, split_, merge_


@pytest.mark.parametrize(
    'dirpath, src, dst, chunk',
    [
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/dup.mov',
            '/mnt/c/Users/estep/Videos/Captures/dup_copy.mov',
            3,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/dup.mov',
            '/mnt/c/Users/estep/Videos/Captures/dup_copy.mov',
            5,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/dup.mov',
            '/mnt/c/Users/estep/Videos/Captures/dup_copy.mov',
            7,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/dup.mov',
            '/mnt/c/Users/estep/Videos/Captures/dup_copy.mov',
            10,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/mgs1.mp4',
            '/mnt/c/Users/estep/Videos/Captures/mgs1_copy.mp4',
            3,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/mgs1.mp4',
            '/mnt/c/Users/estep/Videos/Captures/mgs1_copy.mp4',
            5,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/mgs1.mp4',
            '/mnt/c/Users/estep/Videos/Captures/mgs1_copy.mp4',
            7,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/mgs1.mp4',
            '/mnt/c/Users/estep/Videos/Captures/mgs1_copy.mp4',
            10,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/medium.webm',
            '/mnt/c/Users/estep/Videos/Captures/medium_copy.webm',
            3,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/medium.webm',
            '/mnt/c/Users/estep/Videos/Captures/medium_copy.webm',
            5,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/medium.webm',
            '/mnt/c/Users/estep/Videos/Captures/medium_copy.webm',
            7,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/medium.webm',
            '/mnt/c/Users/estep/Videos/Captures/medium_copy.webm',
            10,
        ),
    ],
)
def test_size(dirpath, src, dst, chunk):
  split_(src, chunk, '')
  merge_(dirpath, True)

  srcfile_size = os.stat(src).st_size
  dstfile_size = os.stat(dst).st_size

  os.remove(dst)

  assert srcfile_size == dstfile_size


@pytest.mark.parametrize(
    'dirpath, src, name, chunk',
    [
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/dup.mov',
            'dup.mov',
            3,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/dup.mov',
            'dup.mov',
            5,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/dup.mov',
            'dup.mov',
            7,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/dup.mov',
            'dup.mov',
            10,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/mgs1.mp4',
            'mgs1.mp4',
            3,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/mgs1.mp4',
            'mgs1.mp4',
            5,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/mgs1.mp4',
            'mgs1.mp4',
            7,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/mgs1.mp4',
            'mgs1.mp4',
            10,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/medium.webm',
            'medium.webm',
            3,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/medium.webm',
            'medium.webm',
            5,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/medium.webm',
            'medium.webm',
            7,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/medium.webm',
            'medium.webm',
            10,
        ),
    ],
)
def test_chunk(dirpath, src, name, chunk):
  split_(src, chunk, '')

  dirpath_ = get_path(dirpath)
  all_parts = list(dirpath_.glob(SPLITTED_PARTS_PATTERN))
  assert len(all_parts) > 0

  splitted = [p for p in all_parts if p.stem == name]
  assert len(splitted) == chunk

  for s in splitted:
    os.remove(s)


@pytest.mark.parametrize(
    'dirpath, src, dst, chunk',
    [
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/dup.mov',
            '/mnt/c/Users/estep/Videos/Captures/dup_copy.mov',
            3,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/dup.mov',
            '/mnt/c/Users/estep/Videos/Captures/dup_copy.mov',
            5,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/dup.mov',
            '/mnt/c/Users/estep/Videos/Captures/dup_copy.mov',
            7,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/dup.mov',
            '/mnt/c/Users/estep/Videos/Captures/dup_copy.mov',
            10,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/mgs1.mp4',
            '/mnt/c/Users/estep/Videos/Captures/mgs1_copy.mp4',
            3,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/mgs1.mp4',
            '/mnt/c/Users/estep/Videos/Captures/mgs1_copy.mp4',
            5,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/mgs1.mp4',
            '/mnt/c/Users/estep/Videos/Captures/mgs1_copy.mp4',
            7,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/mgs1.mp4',
            '/mnt/c/Users/estep/Videos/Captures/mgs1_copy.mp4',
            10,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/medium.webm',
            '/mnt/c/Users/estep/Videos/Captures/medium_copy.webm',
            3,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/medium.webm',
            '/mnt/c/Users/estep/Videos/Captures/medium_copy.webm',
            5,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/medium.webm',
            '/mnt/c/Users/estep/Videos/Captures/medium_copy.webm',
            7,
        ),
        (
            '/mnt/c/Users/estep/Videos/Captures',
            '/mnt/c/Users/estep/Videos/Captures/medium.webm',
            '/mnt/c/Users/estep/Videos/Captures/medium_copy.webm',
            10,
        ),
    ],
)
def test_equal(dirpath, src, dst, chunk):
  split_(src, chunk, '')
  merge_(dirpath, True)

  srcfile = open(src, 'rb')
  dstfile = open(dst, 'rb')

  src_chunk_gen = read_in_chunks(srcfile, BYTES_PER_MB)
  dst_chunk_gen = read_in_chunks(dstfile, BYTES_PER_MB)

  while True:
    src_chunk = next(src_chunk_gen)
    dst_chunk = next(dst_chunk_gen)

    if (src_chunk is None) and (dst_chunk is None):
      break

    assert src_chunk == dst_chunk

  srcfile.close()
  dstfile.close()
  os.remove(dst)
