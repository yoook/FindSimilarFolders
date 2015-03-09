# FindSimilarFolders
find duplicate files and folders, that contain many of them

! This software is still under heavy development and not ready for productive use yet !

This software uses sha1 hashes to create a fingerprint of all files. If two files have the same hash and size, they are regarded to be equal. True equality is NOT checked! There is a tiny chance that due to a hash collision you get false positives!

usage:
fsf.py createIndex	create an indexfile that contains a hash of all your data files

fsf.py collectFolders	create a collectionfile that contains the names of all your folders

fsf.py duplicateFiles	finds duplicate files in the indexfile

fsf.py similarFolders	to be done
