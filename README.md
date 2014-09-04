pyS3fs
======

Mount Amazon's S3 storage as a filesystem.

Installation
------------

pyS3fs is available on PyPi. To install it, make sure you have [fuse"](http://fuse.sourceforge.net/) installed and simply type on your terminal:

```bash
$ pip install pyS3fs
```

Afterwards, setup a config file at ~/.pyS3fs/config with the following contents:

```INI
[global]

AWS_KEY = YOUR_AWS_KEY
AWS_SECRET = YOUR_AWS_SECRET

; Has to be something unique
AWS_BUCKET_NAME = MY_FANCY_UNIQUE_BUCKET_NAME
```

Usage
-----

```bash
$ pyS3fs --help
usage: pyS3fs [-h] [-l {INFO,DEBUG}] [-b] mountpoint

positional arguments:
  mountpoint            directory to mount the filesystem in

optional arguments:
  -h, --help            show this help message and exit
  -l {INFO,DEBUG}, --log-level {INFO,DEBUG}
  -b, --background      run in background
```

Example of usage:

```bash
$ mkdir my_s3_fs

$ pyS3fs my_s3_fs --background
INFO:root:Creating client
INFO:root:Connecting to S3...
INFO:root:Connected.
INFO:root:Getting bucket...
INFO:root:Got bucket.
INFO:root:Creating file tree...
INFO:root:Created.

$ ls my_s3_fs
logs/

$ echo "hello world" > my_s3_fs/new_file # This is actually writing a new file on S3! How cool is that?

$ ls my_s3_fs
logs/  new_file

$ cat my_s3_fs/new_file
hello world
```

License
-------

[MIT](http://opensource.org/licenses/MIT)
