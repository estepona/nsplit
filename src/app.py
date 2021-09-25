import os
from collections import defaultdict
from os.path import abspath, normpath
from pathlib import Path
from time import time

import click
import tqdm

BYTES_PER_KB = 1_024
BYTES_PER_MB = 1_048_576
BYTES_PER_GB = 1_073_741_824

MAX_BUFFER_SIZE = BYTES_PER_MB * 16

KB_SUFFIX_LOWERCASE = 'kb'
MB_SUFFIX_LOWERCASE = 'mb'
GB_SUFFIX_LOWERCASE = 'gb'

SPLITTED_PARTS_PATTERN = '*.*.p*'

START_TIME = time()


def get_time_passed() -> int:
  return int(time() - START_TIME)


def get_path(path: str) -> Path:
  return Path(abspath(normpath(path)))


def read_in_chunks(file_object, chunk_size: int):
  while True:
    data = file_object.read(chunk_size)
    if not data:
      yield None
      break

    yield data


def write_splitted_video(path: str, part: int, data: bytes):
  filename = get_path(f'{path}.p{part}')
  with open(filename, 'wb') as pf:
    pf.write(data)
    click.echo(f'[{get_time_passed()}s] generated {filename}')


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
  cur_l = 0
  part = 1

  src_file = open(src, 'rb')
  dst_file = open(f'{src}.p{part}', 'wb')
  pbar = tqdm.tqdm(total=chunk)

  for cnk in read_in_chunks(src_file, chunk_size):
    if cur_l == spc:
      dst_file.close()
      pbar.update(1)

      dst_file = open(f'{src}.p{part + 1}', 'wb')

      cur_l = 0
      part += 1

    if cnk is not None:
      cnk_l = len(cnk)
      if cur_l < spc:
        if cur_l + cnk_l > spc:
          dst_file.write(cnk[:spc - cur_l])
          dst_file.close()
          pbar.update(1)

          dst_file = open(f'{src}.p{part + 1}', 'wb')
          dst_file.write(cnk[spc - cur_l:])

          cur_l = cnk_l - (spc-cur_l)
          part += 1
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
  """ Split the video into several chunks by specifying EITHER:\n
  - number of chunks with --chunk flag\n
  - size of each chunk and the number of chunks is calculated accordingly, i.e. 5kb, 10mb, 1gb

  SRC is the file path of the video to be splitted.
  """
  split_(src, chunk, size_per_chunk)


def merge_(src: str, remove: bool):
  dirpath = get_path(src)

  all_parts = list(dirpath.glob(SPLITTED_PARTS_PATTERN))
  if not all_parts:
    click.echo('no splitted video parts found')
    return

  videos = defaultdict(list)
  for p in all_parts:
    name = p.stem
    videos[name].append(p)

  video_names = list(videos.keys())
  if len(video_names) >= 2:
    question = f'found {len(video_names)} splitted videos, choose one to proceed:\n'
    for i, v in enumerate(video_names):
      question += f'{i+1} - {v}\n'
    question += 'your answer'

    video_choice = click.prompt(question, type=int)
    while (video_choice > len(video_names)) or (video_choice < 1):
      video_choice = click.prompt('incorrect input, please try again', type=int)
    video = video_names[video_choice - 1]
  else:
    video = video_names[0]

  parts = sorted(videos[video], key=lambda x: int(x.suffix.split('p')[1]))
  pbar = tqdm.tqdm(total=len(parts))

  dst = parts[0].parent / parts[0].stem
  if dst.is_file():
    filename = parts[0].stem.split('.')[0]
    extension = parts[0].stem.split('.')[1]
    dst = parts[0].parent / f'{filename}_copy.{extension}'

  dst_file = open(dst, 'wb')
  for p in parts:
    p_size = os.stat(p).st_size
    with open(p, 'rb') as f:
      for cnk in read_in_chunks(f, min(p_size, MAX_BUFFER_SIZE)):
        if cnk:
          dst_file.write(cnk)
    pbar.update(1)

  dst_file.close()
  pbar.close()
  click.echo(f'merged splitted files to {dst}')

  if remove:
    for p in parts:
      os.remove(p)
    click.echo('removed splitted files')


@cli.command()
@click.argument('src', nargs=1, type=click.Path(exists=True))
@click.option('-r', '--remove', default=False, is_flag=True, help='remove splitted files after merge')
def merge(src: str, remove: bool):
  """ Merge NVP splitted videos into one.

  NVP splitted videos can be identified with '.p1', '.p2' (etc.) appended to the original video's name (path).

  If multiple videos that are splitted are found, user can choose which one to merge.

  SRC is the directory path that contains (parent to) splitted videos.
  """
  merge_(src, remove)


if __name__ == '__main__':
  # pylint: disable=no-value-for-parameter
  cli()
