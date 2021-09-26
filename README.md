<div align=center>
  <h1>Naive File Splitter</h1>
  <img src="https://img.shields.io/badge/nfs--estepona-0.2.*-blue"/>
  <img src="https://img.shields.io/badge/python->=3.5-blueviolet"/>
  <img src="https://img.shields.io/badge/click-7.0-brightgreen"/>
</div>

Naive File Splitter (NFS) is a simple CLI tool to split a file into several smaller chunks at data level and merge them back. It does not compress or transform the original file in any way. NFS only reads the file in binary stream and writes it into chunks whose number or size is given by the user.

By having smaller chunks of a file instead of a large one, it allows easier and faster data download and upload, and bypasses file size limits inplaced by some cloud providers.

NFS works with *any* file format.

## Install

NFS requires *Python >= 3.5*.

`pip install nfs-estepona`

Upon installation, a new `nfs` binary will be added to system's path.

## Command

### Split

#### Usage

`nfs split [OPTIONS] SRC`

Split the file into several chunks by specifying EITHER:
- number of chunks with `--chunk` flag
- size of each chunk with `--size-per-chunk` flag, and the number of chunks is calculated accordingly, i.e. *5kb*, *10mb*, *1gb*

`SRC` is the filepath.

Options:
- `-c, --chunk`, *INTEGER*, number of chunks to output
- `-s, --size-per-chunk`, *TEXT*, size of each chunk

#### Example

##### Split a file into 5 chunks

`nfs split -c 5 /mnt/c/Users/estep/Videos/Captures/mgs1.mp4`

```bash
$ nfs split -c 5 /mnt/c/Users/estep/Videos/Captures/mgs1.mp4 -c 5
100%|█████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:00<00:00, 37.28it/s]
splitted /mnt/c/Users/estep/Videos/Captures/mgs1.mp4 into 5 chunks
```

##### Split a file into chunks of 25MB each

`nfs split -s 25mb /mnt/c/Users/estep/Videos/Captures/medium.webm`

```bash
$ nfs split -s 25mb /mnt/c/Users/estep/Videos/Captures/medium.webm
100%|███████████████████████████████████████████████████████████████████████████████████| 18/18 [00:08<00:00,  2.00it/s]
splitted /mnt/c/Users/estep/Videos/Captures/medium.webm into 18 chunks
```

### Merge

#### Usage

`nfs merge [OPTIONS] SRC`

Merge NFS splitted file chunks into one.

NFS splitted file chunks can be identified with *.c1*, *.c2* (etc.) appended to the end of original file's name (path).

If multiple files that are splitted are found, user can choose which one to merge.

If the original file exists under the same directory, a new file with *_copy* appended to the filename will be created.

`SRC` is the directory path that contains (parent to) splitted file chunks.

Options:
- `-r, --remove`, remove splitted file chunks after merge

#### Example

##### Merge splitted file chunks into one

`nfs merge /mnt/c/Users/estep/Videos/Captures`

```bash
$ nfs merge /mnt/c/Users/estep/Videos/Captures
100%|█████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:00<00:00, 50.87it/s]
merged splitted file chunks to /mnt/c/Users/estep/Videos/Captures/mgs1_copy.mp4
```
##### Merge splitted file chunks into one and remove chunks

`nfs merge -r /mnt/c/Users/estep/Videos/Captures`

```bash
$ nfs merge -r /mnt/c/Users/estep/Videos/Captures
100%|█████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:00<00:00, 49.96it/s]
merged splitted file chunks to /mnt/c/Users/estep/Videos/Captures/mgs1_copy.mp4
removed splitted file chunks
```

##### Merge splitted file chunks into one where chunks of other files exist

`nfs merge /mnt/c/Users/estep/Videos/Captures`

```bash
$ nfs merge /mnt/c/Users/estep/Videos/Captures
found 2 splitted file chunks, choose one to proceed:
1 - dup.mov
2 - mgs1.mp4
your answer: 2
100%|█████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:00<00:00, 47.95it/s]
merged splitted file chunks to /mnt/c/Users/estep/Videos/Captures/mgs1_copy.mp4
```

## Author

[Binghuan Zhang](https://github.com/estepona) - esteponawondering@gmail.com

## LICENSE

MIT
