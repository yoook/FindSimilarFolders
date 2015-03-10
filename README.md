# FindSimilarFolders
find duplicate files and folders, that contain many of them

**! This software is still under heavy development and not ready for productive use yet !**

*This software uses sha1 hashes to create a fingerprint of all files.
If two files have the same hash and size, they are regarded to be equal.
True equality is NOT checked! There is a tiny chance that due to a hash collision you get false positives!*

##usage:
**fsf.py createIndex**	or **fsf.py ci**  create an indexfile that contains a hash of all your data files

**fsf.py collectFolders**	or **fsf.py cf**  create a collectionfile that contains the names of all your folders

**fsf.py duplicateFiles**	or **fsf.py df**  finds duplicate files in the indexfile

**fsf.py similarFolders**	or **fsf.py sf**  *to be done*

##File types
###indexfile
produced by **fsf.py createIndex**<br>
contains 4 tab-separated columns<br>
example:

size  | mtime           |              hash                        | path
-----:|----------------:|:----------------------------------------:|:------
`383` |`1425734526.3954`|`b8e70a943cb82fd03805fb42e31857ea24aa40bb`|`path/to/file`
 
###collection file
produced by **fsf.py collectFolders**<br>
contains 4 tab-separated columns<br>
 
serial number | path         | # elements | # files
-------------:|:------------:|:----------:|:--------------:
 `1`          |`/path/to/dir`| `8`        |  `5`
 
the second last column counts the total number of elements (but not subfolders) in the
folder while the last column only counts accessable files. It excludes
links and files that you don't have the permission to read
 
###duplicates file 
produced by **fsf.py duplicateFiles**
contains blocks of several lines. Blocks are separated by blank lines.<br>
the lines inside the blocks contain of several tab-separated columns:<br>
* the first line of each block contains of the `size` and the `hash`of all files in this block
* all other lines list duplicate files. they contain of `mtime`, `filename` and `path`of the files

example:
```
  42        b8e70a943cb82fd03805fb42e31857ea24aa40bb
1425734526.3954  filename1  /path/to/first/file
1425755949.3846  filename2  /path/to/second/file
1289468796.4897  filename3  /a/different/path/to/the/third/file
```

###similar folders
*to be done*

##Notes:
