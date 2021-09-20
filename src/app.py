from os.path import abspath, normpath
from pathlib import Path

import click

BYTES_PER_KB = 1_024
BYTES_PER_MB = 1_048_576
BYTES_PER_GB = 1_073_741_824

KB_SUFFIX_LOWERCASE = 'kb'
MB_SUFFIX_LOWERCASE = 'mb'
GB_SUFFIX_LOWERCASE = 'gb'


def get_path(path: str) -> Path:
  return Path(abspath(normpath(path)))


@click.group()
def cli():
  return


@cli.command()
@click.argument('src', nargs=1, type=click.Path(exists=True))
@click.option('-c', '--chunk', type=int, help='number of chunks to output')
@click.option('-s', '--size-per-chunk', type=str, help='size of each chunk')
def split(src: click.Path, chunk: int, size_per_chunk: str):
  """ Split the video into several chunks by specifying EITHER:\n
  - number of chunks with --chunk flag\n
  - size of each chunk and the number of chunks is calculated accordingly, i.e. 5kb, 10mb, 1gb
  """
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

  with open(src, 'rb') as file:
    data = file.read()

  size = len(data)
  chunk_indexes = []

  if use_chunk:
    spc = size // chunk
  else:
    spc_num = int(size_per_chunk[:-2])
    spc_unit = size_per_chunk[-2:].lower()

    if spc_unit == KB_SUFFIX_LOWERCASE:
      spc = spc_num * BYTES_PER_KB
    elif spc_unit == MB_SUFFIX_LOWERCASE:
      spc = spc_num * BYTES_PER_MB
    elif spc_unit == GB_SUFFIX_LOWERCASE:
      spc = spc_num * BYTES_PER_GB

  start = 0
  end = spc
  while size > 0:
    chunk_indexes.append((start, end))
    start += spc
    end += spc
    size -= spc

  for i, (start_, end_) in enumerate(chunk_indexes):
    filename = get_path(f'{src}.p{i+1}')
    with open(filename, 'wb') as file:
      file.write(data[start_:end_])
      click.echo(f'generated {filename}')


@cli.command()
@click.argument('src', nargs=-1, type=click.Path(exists=True))
def merge(src: click.Path):
  return


if __name__ == '__main__':
  # pylint: disable=no-value-for-parameter
  cli()
