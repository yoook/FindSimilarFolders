# FindSimilarFolders: find duplicate files and folders, that contain many of them
# Copyright (C) 2015  Johannes König

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import hashlib
import pathlib
import sys

from time import process_time	# todo: remove later, only needed for optimisation
import resource					# for memory monitoring. might be removed later

def _gethash(filename, blocksize=65536):
	hasher=hashlib.sha1()
	with open(filename, "rb") as f:
		for block in iter(lambda: f.read(blocksize), b''):
			hasher.update(block)
	return hasher.hexdigest()


def create_index(rootdir, outfile, errorfile, start_at="", start_after=True, exclude=[], exclude_pattern=[], rel_to=None, size_digits=13, verbosity=2):
	""" walk down the tree from rootdir (exclude 'exclude'. start at 'start_at' to continue
	a previous run (if Start_after==True, start with the next file, otherwise start with the given file))
	for each file calculate its checksum. append file statistics to 'outfile'
	as follows, separated by "\t":
	filesize (use 'sizedigits' digits)	mtime	checksum	path (relative to 'relto')
	if verbosity =  0: print nothing
					1: print each folder
					2: print each file
					3: print each line """

	#todo: make 'start_at' find its start faster


	start_at_file = start_at and os.path.isfile(start_at)
	start_at_dir  = start_at and os.path.isdir(start_at)
	show_message  = True


	# walk through the whole tree
	for root, dirs, files in os.walk(rootdir):
		if verbosity == 1:
			print(root)
		if verbosity > 1:
			print('\033[93m' + root + '\033[0m')


		# skip until reach start_at (or dir after)
		if start_at_dir:
			if verbosity >= 1 and show_message:
				print("\033[94mskip until dir " + start_at + "\033[0m")
				show_message = False
			if os.path.samefile(root, start_at):
				start_at_dir = False
				print("\033[94mskipping to dir finished\033[0m")
				show_message = True
				if start_after:
					dirs.clear()
					continue
			else:
				continue


		# skip dirs, that match with exclude (and subdirs)
		if exclude:
			for path in exclude:
				if os.path.samefile(root, path):
					if verbosity >= 1:
						print("\033[94mexlude dir: " + path + "\033[0m")
					dirs.clear()
					files.clear()
					continue



		for name in files:
			fullname = os.path.join(root, name)

			if start_at_file:	# skip until reach start_at (or file after)
				if verbosity >= 1 and show_message:
					print("\033[94mskip until file " + start_at + "\033[0m")
					show_message = False
				if os.path.exists(fullname) and os.path.samefile(fullname, start_at):
					start_at_file = False
					print("\033[94mskipping to file finished\033[0m")
					show_message = True
					if start_after:
						continue
				else:
					continue

			if os.path.islink(fullname):		# don't resove links
				if verbosity >= 2:
					print("\033[94mis link: " + fullname + "\033[0m")
				continue
			if not os.path.isfile(fullname):	# is it a file at all?
				if verbosity >= 2:
					print("\033[94mnot a file: " + fullname + "\033[0m")
				continue



			if exclude_pattern:			# skip files, that match with exclude_pattern
				skip=False
				for pattern in exclude_pattern:
					if pathlib.Path(fullname).match(pattern):
						if verbosity >= 2:
							print("\033[94mexclude file " + name + ", matches pattern ", pattern, "\033[0m")
						skip=True
				if skip:
					continue


			fstats = os.stat(fullname)

			try:
				fhash = _gethash(fullname)

			except PermissionError as e:
				print ("\033[91mPermission Error: " + fullname + "\033[0m")
				if errorfile:
					with open(errorfile, "a") as errf:
						errf.write("Permission Error: "+ fullname + "\n")
				continue

			except FileNotFoundError as e:
				print ("\033[91mFile not found Error: " + fullname + "\033[0m")
				if errorfile:
					with open(errorfile, "a") as errf:
						errf.write("file not found Error: "+ fullname + "\n")
				continue

			except Exception as e:
				print ("\033[91munhandled Exception: " + fullname + "\033[0m")
				errstr = str(e)
				if errorfile:
					with open(errorfile, "a") as errf:
						errf.write(fullname + "  " + errstr + "\n")
				continue


			line = "{size: {digits}d}\t{mtime: 10.4f}\t{checksum}\t{path}".format(
				digits = size_digits,
				size = fstats.st_size,
				mtime = fstats.st_mtime,
				checksum = fhash,
				path = ( os.path.relpath(fullname, rel_to) if rel_to!=None else fullname))

			outfile.write(line+'\n')

			if verbosity == 2:
				print(name)
			if verbosity >= 3:
				print(line)



def collect_folders(rootdir, outfile, start_at="", start_after=True, exclude=[], exclude_pattern=[], rel_to=None, fast=False, size_digits=6, verbosity=2, serial = 1):
	""" walk down the tree from rootdir (exclude 'exclude'. start at 'start_at' to continue
	a previous run (if Start_after==True, start with the next file, otherwise start with the given file))
	for each folder count its files. append file statistics to 'outfile'
	as follows, separated by "\t":
	serial number		path (relative to 'relto')	number of items		number of readable files
	if verbosity =  0: print nothing
					1: print each folder
					2: print each folder messages
					3: print each line """

	#todo: make 'start_at' find its start faster


	start_at_file = start_at and os.path.isfile(start_at)
	start_at_dir  = start_at and os.path.isdir(start_at)
	show_message  = True
	serial -= 1

	if start_at_file:
		raise ValueError('start_at has to be a dir, not a file!')


	# walk through the whole tree
	for root, dirs, files in os.walk(rootdir):
		if verbosity == 1:
			print(root)
		if verbosity > 1:
			print('\033[93m' + root + '\033[0m')


		# skip until reach start_at (or dir after)
		if start_at_dir:
			if verbosity >= 1 and show_message:
				print("\033[94mskip until dir " + start_at + "\033[0m")
				show_message = False
			if os.path.samefile(root, start_at):
				start_at_dir = False
				print("\033[94mskipping to dir finished\033[0m")
				show_message = True
				if start_after:
					dirs.clear()
					continue
			else:
				continue


		# skip dirs, that match with exclude (and subdirs)
		if exclude:
			skip=False
			for path in exclude:
				if os.path.samefile(root, path):
					if verbosity >= 1:
						print("\033[94mexlude dir: " + path + "\033[0m")
					dirs.clear()
					files.clear()
					skip=True
			if skip:
				continue

		number_real_files=0
		if not fast:
			for name in files:
				fullname = os.path.join(root, name)

				if os.path.islink(fullname):		# don't resove links
					if verbosity >= 2:
						print("\033[94mis link: " + fullname + "\033[0m")
					continue
				if not os.path.isfile(fullname):	# is it a file at all?
					if verbosity >= 2:
						print("\033[94mnot a file: " + fullname + "\033[0m")
					continue

				if exclude_pattern:			# skip files, that match with exclude_pattern
					skip=False
					for pattern in exclude_pattern:
						if pathlib.Path(fullname).match(pattern):
							if verbosity >= 2:
								print("\033[94mexclude file " + name + ", matches pattern ", pattern, "\033[0m")
							skip=True
					if skip:
						continue

				number_real_files += 1

		serial += 1
		line = "{serial: {serdigits}d}\t{path}\t{numfiles: {digits}d}\t{numrealfiles: {digits}d}".format(
					serdigits = size_digits + 3,
					digits = size_digits,
					serial = serial,
					numfiles = len(files),
					numrealfiles = -1 if fast else number_real_files,
					path = ( os.path.relpath(root, rel_to) if rel_to!=None else root))

		outfile.write(line+'\n')
		if verbosity >= 3:
			print(line)



def _get_fileinfo(string):
	splitstring = string.rstrip('\n').split('\t', 3)		# if for any reason the filename contains '\t', we don't have a problem ;-)
	path = pathlib.PurePath(splitstring[3])

	#		size                    mtime                  hash                    path         filename
	return (splitstring[0].strip(), float(splitstring[1]), splitstring[2].strip(), path.parent, path.name)


def find_duplicate_files(indexfiles, outfile, size_digits=13, verbosity=1):
	""" read all indexfiles into one large list,
	sort this list by the hashes and filesizes
	and print all duplicates to the outfile"""

	filelist = []

	# read all indexfiles
	if verbosity >= 1: print ("reading files...")
	for file in indexfiles:
		if verbosity >= 2:
			print(file)
		with open(file, 'r') as f:
			for line in f:
				filelist.append(_get_fileinfo(line))

	# sort files
	if verbosity >=1: print("sorting files by size and checksum...")
	filelist.sort(key = lambda x: x[0].rjust(size_digits) + ' ' + x[2]) # sort my "size<space>hash"

	# search for duplicates
	if verbosity >=1: print("searching for duplicates...")
	old_entry = ("", 0., "", "")
	first = True
	for entry in filelist:
		if entry[0] == old_entry[0] and entry[2] == old_entry[2]:
			line = ""
			if first:
				line += '\n'  + entry[0].rjust(size_digits) + '\t' + entry[2] + '\n'
				line += "{mtime:10.4f}\t{name}\t{path}\n".format(mtime=old_entry[1], path=old_entry[3], name=old_entry[4])
				first = False
			line +="{mtime:10.4f}\t{name}\t{path}\n".format(mtime=entry[1], path=entry[3], name=entry[4])
			outfile.write(line)
			if verbosity >= 3: print(line)
		else:
			first = True
		old_entry = entry


def find_similar_folders(indexfiles, outfile, size_digits=13, verbosity=1):
	""" read all indexfiles into one large list,
	sort this list by the hashes and filesizes
	and print all duplicates to the outfile"""

	#todo: somehow handle identical files in one folder, as they mess up everything a bit

	filelist = []

	# read all indexfiles
	if verbosity >= 1: print ("reading files...")
	for file in indexfiles:
		if verbosity >= 1:
			print(file)
		with open(file, 'r') as f:
			for line in f:
				filelist.append(_get_fileinfo(line))

	# filelist now contains tupel(size, mtime, hash, path, filename) of all files read


	# sort files, reverse order
	if verbosity >=1: print("sorting files by size and checksum...")
	filelist.sort(key = lambda x: x[0].rjust(size_digits) + '_' + x[2], reverse=True ) # sort by "size_hash"

	# search for duplicates
	if verbosity >=1: print("searching for duplicates...")
	prev_entry = ("", 0., "", "")
	first = True
	doublelist = []
	tmplist=[]
	while filelist:
		entry = filelist.pop()
		if entry[0] == prev_entry[0] and entry[2] == prev_entry[2]:
			if first:
				first = False
				tmplist.append((prev_entry[3], prev_entry[4]))	#safe just path+name to a new list
			tmplist.append((entry[3], entry[4]))
		else:
			first = True
			if tmplist:
				tmplist.sort()
				doublelist.append(tmplist.copy())	# make a copy of tmplist!
				tmplist.clear()
		prev_entry = entry

	if tmplist:
		tmplist.sort()
		doublelist.append(tmplist.copy())	# make a copy of tmplist!
		tmplist.clear()

	del(filelist) # might be unneccessary, as filelist should be empty by now anyway, but might help garbage collction

	# doublelist now contains sublists.
	# each sublist contains tupel(path, filename) of identical files
	# each sublist is sorted by the path


	# "transpose" the sublists of doublelist and save as combined_long
	if verbosity >= 1:
		print("transforming list of duplicates...")

	combined_long = []
	while doublelist:
		entry = doublelist.pop()
		combined_long.append([[i[0] for i in entry], [i[1] for i in entry]])

	del(doublelist)	#might be unneccessary, as doublelist should be empty by now anyway, but might help garbage collction

	# combined_long now contains sublists.
	# each sublist is [[path/to/file1, path/to/file2, path/to/file3, ...], [file1, file2, file3, ...]]

	if verbosity >= 1:
		print("sorting list of duplicats by their folders...")

	combined_long.sort(key = lambda x: x[0]) # sort BY list of paths (NOT: sort THE list of paths)

	# combined_long is now sorteted by the complete tuple (i.e. sublist) of paths


	# collect different files of the same folders in one list, save as combined
	if verbosity >=1: print("collecting duplicates of same folder...")
	entry = combined_long.pop()
	tmplist=[]
	tmppaths=[]
	combined = []

	while combined_long:
		next_entry = combined_long.pop()
		tmppaths = entry[0].copy()
		tmplist.append(entry[1])

		if entry[0] != next_entry[0]:
			combined.append([tmppaths.copy(), tmplist.copy()])
			tmppaths.clear()
			tmplist.clear()

		entry = next_entry

	tmppaths = entry[0].copy()
	tmplist.append(entry[1])
	combined.append([tmppaths.copy(), tmplist.copy()])
	tmppaths.clear()
	tmplist.clear()

	del(combined_long)

	# combined now contains two-element sublists
	# the first element of the sublist is a (subsub)list containing the paths of all involved folders
	# the second element is a subsublist containing subsubsublists of identical files
	# one element of combined looks like:
	# [[path/to/folder1, path/to/folder2, path/to/folder3, ...], [[file1, file2, file3, ...], [filea, fileb, filec, ...], [filex, filey, filez, ...], ... ]]
	# where file1-3 are identical (filea-c and filex-z respectively)
	# and file1, filea and filex are in folder1 (file[2,b,y] in folder2 and file[3,c,z] in folder 3)


	# put this out only if you want the combined list
	'''
	if verbosity >= 1:
		print("output...")
		if verbosity >= 2:
			print()


	for dupset in combined:
		line = ""
		for path in dupset[0]:
			line += str(path) + '\n'
		if verbosity == 2:
			print(line)
		line += "--------\n"
		for files in dupset[1]:
			for file in files:
				line += file + '\t'
			line.rstrip('\t')
			line += '\n'
		line += '\n'
		if verbosity >= 3:
			print(line)

		outfile.write(line)
	'''


	# break the (potentially long) tupel of different folders with same files from 'combined'
	# into pairs, stored in 'paired_long'
	infotext = "combining folders to pairs..."
	if verbosity >= 1:
		sys.stdout.write(infotext)
		sys.stdout.flush()

	paired_long = []
	ready =  len(combined)


	# todo: this consumes loads of memory! make it more efficient or use hdd instead
	while combined:
		tmppaths, tmpfiles = combined.pop()		# todo: remove 0 -> pop(), not pop(0), might be faster

#		print(tmppaths)
#		print(tmpfiles)
#		print('\n')
	#	i = 0
	#	for path_i in tmppaths:
	#		j = 0
	#		for path_j in tmppaths:
	#			if j <= i:
	#				j += 1
	#				continue
				#paired_long.append([(path_i, path_j), [(f[i],f[j]) for f in tmpfiles]])
	#			paired_long.append([(tmppaths[i], tmppaths[j]), [(f[i], f[j]) for f in tmpfiles]])
	#			j += 1
	#		i += 1

		for i in range(len(tmppaths)):
			for j in range(i+1, len(tmppaths)):
	#			pass
				paired_long.append([(tmppaths[i], tmppaths[j]), [(f[i], f[j]) for f in tmpfiles]])
	#			paired_long.append([(tmppaths[i], tmppaths[j]), list(zip(*list(zip(*tmpfiles))[i:j+1:j-i]))])

		tmppaths.clear()
		tmpfiles.clear()
		if verbosity >= 1:
			sys.stdout.write('\r'+infotext + "  " + str(round((1 - float(len(combined))/ready) * 100, 1)) + " %  " + \
						str(round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 )) + " MB  " )
			sys.stdout.flush()

	if verbosity >= 1:
		print('\r' + infotext + "         ")
	del(combined)


	# paired_long is similar to combined, but with only 2 folders. one element of paired_long looks like:
	# [(path/to/folder1, path/to/folder2), [(file1, file2), (filea, fileb), (filex, filey), ...]]


	if verbosity >= 1:
		print("sorting list of pairs by folders...")

	paired_long.sort(key=lambda x:x[0])


	# combine files of identical folder-pairs
	infotext = "combining identical pairs..."

	if verbosity >= 1:
		sys.stdout.write(infotext)
		sys.stdout.flush()

	paired = []
	ready = len(paired_long)
	i = 0

	if len(paired_long) >= 2:
		prev_entry = paired_long.pop()
		tmplist = prev_entry[1]
		entry = []
		while paired_long:
			entry = paired_long.pop()
			if prev_entry[0] == entry[0]:
				tmplist.extend(entry[1])
			else:
				paired.append([prev_entry[0], tmplist.copy()])
				tmplist.clear()
				tmplist = entry[1]

			prev_entry = entry
			if verbosity >= 1 and i > 100:
				sys.stdout.write('\r'+infotext + "  " + str(round((1 - float(len(paired_long))/ready) * 100, 1)) + " %" + \
						str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 ) + " MB")
				sys.stdout.flush()
				i = 0
			i += 1

		if prev_entry[0] == entry[0]:
			paired.append([prev_entry[0], tmplist.copy()])
		else:
			paired.append([entry[0], entry[1]])

	else:
		paired = paired_long.copy()

	if verbosity >= 1:
		print('\r' + infotext + "                  ")
	del(paired_long)

	# the structure of 'paired' is identical to 'paired_long'. The difference is, that 'paired_long' may contain
	# the same pair of paths several times and in 'paired' each pair of paths exists only once with all files
	# collected in this entry


	if verbosity >= 1:
		print("output...")
		if verbosity >= 2:
			print()


	for dupset in paired:
		line = str(dupset[0][0]) + '\n' + str(dupset[0][1]) + '\n'
		if verbosity == 2:
			print(line)
		line += "--------\n"
		for files in dupset[1]:
			line += files[0] + '\t' + files[1] + '\n'
		line += '\n'
		if verbosity >= 3:
			print(line)

		outfile.write(line)


# todo: whenever combining something: check, that list is long enough
