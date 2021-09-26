import os
from collections import defaultdict
from os.path import abspath, normpath
from pathlib import Path

import click
import tqdm

BYTES_PER_KB = 1_024
BYTES_PER_MB = 1_048_576
BYTES_PER_GB = 1_073_741_824

MAX_BUFFER_SIZE = BYTES_PER_MB * 16

KB_SUFFIX_LOWERCASE = 'kb'
MB_SUFFIX_LOWERCASE = 'mb'
GB_SUFFIX_LOWERCASE = 'gb'

SPLITTED_CHUNKS_PREFIX = 'c'
SPLITTED_CHUNKS_PATTERN = '*.*.c*'


def get_path(path: str) -> Path:
  return Path(abspath(normpath(path)))


def read_in_chunks(file_object, chunk_size: int):
  while True:
    data = file_object.read(chunk_size)
    if not data:
      yield None
      break

    yield data


@click.group()
def cli():
  return


def split_(src: str, chunk: int, size_per_chunk: str):
  if (not chunk) and (not size_per_chunk):
    click.echo('either --chunk or --size-per-chunk should be provided')
    return
  if chunk and chunk <= 1:
    click.echo('--chunk has to be greater than 1')
    return
  if size_per_chunk:
    if (len(size_per_chunk) <= 2) or\
       (size_per_chunk[-2:].lower() not in {KB_SUFFIX_LOWERCASE, MB_SUFFIX_LOWERCASE, GB_SUFFIX_LOWERCASE}):
      click.echo('--chunk-per-size has to end with kb/KB, mb/MB, or gb/GB')
      return
    elif int(size_per_chunk[:-2]) <= 0:
      click.echo('--chunk-per-size has to be greater than 0')
      return

  if chunk and size_per_chunk:
    click.echo('both --chunk and --size-per-chunk provided, using --chunk...')
  use_chunk = bool(chunk)

  src_size = os.stat(src).st_size

  if use_chunk:
    spc = (src_size // chunk) if (src_size % chunk == 0) else (src_size//chunk + 1)
  else:
    spc_num = int(size_per_chunk[:-2])
    spc_unit = size_per_chunk[-2:].lower()

    if spc_unit == KB_SUFFIX_LOWERCASE:
      spc = spc_num * BYTES_PER_KB
    elif spc_unit == MB_SUFFIX_LOWERCASE:
      spc = spc_num * BYTES_PER_MB
    elif spc_unit == GB_SUFFIX_LOWERCASE:
      spc = spc_num * BYTES_PER_GB

    chunk = (src_size // spc) if (src_size % spc == 0) else (src_size//spc + 1)

  chunk_size = min(spc, MAX_BUFFER_SIZE)
  chunk_index = 1
  cur_l = 0

  src_file = open(src, 'rb')
  dst_file = open(f'{src}.{SPLITTED_CHUNKS_PREFIX}{chunk_index}', 'wb')
  pbar = tqdm.tqdm(total=chunk)

  for cnk in read_in_chunks(src_file, chunk_size):
    if cur_l == spc:
      dst_file.close()
      pbar.update(1)

      dst_file = open(f'{src}.{SPLITTED_CHUNKS_PREFIX}{chunk_index + 1}', 'wb')

      cur_l = 0
      chunk_index += 1

    if cnk is not None:
      cnk_l = len(cnk)
      if cur_l < spc:
        if cur_l + cnk_l > spc:
          dst_file.write(cnk[:spc - cur_l])
          dst_file.close()
          pbar.update(1)

          dst_file = open(f'{src}.{SPLITTED_CHUNKS_PREFIX}{chunk_index + 1}', 'wb')
          dst_file.write(cnk[spc - cur_l:])

          cur_l = cnk_l - (spc-cur_l)
          chunk_index += 1
        else:
          dst_file.write(cnk)
          cur_l += cnk_l

  src_file.close()
  if dst_file:
    if dst_file.tell() == 0:
      dst_file.close()
      os.remove(dst_file.name)
    else:
      dst_file.close()
      pbar.update(1)
  pbar.close()
  click.echo(f'splitted {src_file.name} into {chunk} chunks')


@cli.command()
@click.argument('src', nargs=1, type=click.Path(exists=True))
@click.option('-c', '--chunk', type=int, help='number of chunks to output')
@click.option('-s', '--size-per-chunk', type=str, help='size of each chunk')
def split(src: str, chunk: int, size_per_chunk: str):
  """ Split the file into several chunks by specifying EITHER:\n
  - number of chunks with --chunk flag\n
  - size of each chunk with --size-per-chunk flag, and the number of chunks is calculated accordingly, i.e. 5kb, 10mb, 1gb

  SRC is the filepath.
  """
  split_(src, chunk, size_per_chunk)


def merge_(src: str, remove: bool):
  dirpath = get_path(src)

  all_chunks = list(dirpath.glob(SPLITTED_CHUNKS_PATTERN))
  if not all_chunks:
    click.echo('no splitted file chunks found')
    return

  files = defaultdict(list)
  for c in all_chunks:
    name = c.stem
    files[name].append(c)

  file_names = list(files.keys())
  if len(file_names) >= 2:
    question = f'found {len(file_names)} splitted file chunks, choose one to proceed:\n'
    for i, v in enumerate(file_names):
      question += f'{i+1} - {v}\n'
    question += 'your answer'

    file_choice = click.prompt(question, type=int)
    while (file_choice > len(file_names)) or (file_choice < 1):
      file_choice = click.prompt('incorrect input, please try again', type=int)
    file = file_names[file_choice - 1]
  else:
    file = file_names[0]

  chunks = sorted(files[file], key=lambda x: int(x.suffix.split(SPLITTED_CHUNKS_PREFIX)[1]))
  pbar = tqdm.tqdm(total=len(chunks))

  dst = chunks[0].parent / chunks[0].stem
  if dst.is_file():
    filename = chunks[0].stem.split('.')[0]
    extension = chunks[0].stem.split('.')[1]
    dst = chunks[0].parent / f'{filename}_copy.{extension}'

  dst_file = open(dst, 'wb')
  for c in chunks:
    p_size = os.stat(c).st_size
    with open(c, 'rb') as f:
      for cnk in read_in_chunks(f, min(p_size, MAX_BUFFER_SIZE)):
        if cnk:
          dst_file.write(cnk)
    pbar.update(1)

  dst_file.close()
  pbar.close()
  click.echo(f'merged splitted file chunks to {dst}')

  if remove:
    for c in chunks:
      os.remove(c)
    click.echo('removed splitted file chunks')


@cli.command()
@click.argument('src', nargs=1, type=click.Path(exists=True))
@click.option('-r', '--remove', default=False, is_flag=True, help='remove splitted file chunks after merge')
def merge(src: str, remove: bool):
  """ Merge NFS splitted file chunks into one.

  NFS splitted file chunks can be identified with '.c1', '.c2' (etc.) appended to the end of original file's name (path).

  If multiple files that are splitted are found, user can choose which one to merge.

  If the original file exists under the same directory, a new file with '_copy' appended to the filename will be created.

  SRC is the directory path that contains (parent to) splitted file chunks.
  """
  merge_(src, remove)


if __name__ == '__main__':
  # pylint: disable=no-value-for-parameter
  cli()
