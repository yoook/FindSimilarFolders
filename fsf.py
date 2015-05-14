#!/usr/bin/env python3

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

# verbosity guidelines:
# 	0:	print nothing except errors
#	1:	print rought progress
#	2:	print detailed progress
#	3:	print everything

#todo: harden commandline interface: don't crash, if called with invalid/none options/arguments

import argparse

from fsf_core import create_index, collect_folders, find_duplicate_files, find_similar_folders


def prepare_create_index(args):	#todo: integrate collect_folders in create_index
	print('create_index')

	if args.exclude_path:
		exclude = [item for sublist in args.exclude_path for item in sublist]	#flatten list of lists
	else:
		exclude = None

	if args.exclude_pattern:
		exclude_pattern = [item for sublist in args.exclude_pattern for item in sublist]
	else:
		exclude_pattern = None

	if args.start_with:
		start_at = args.start_with
		start_after=False
	elif args.start_after:
		start_at = args.start_after
		start_after=True
	else:
		start_at = ""
		start_after=True

	for rootdir in args.rootdir:
		with open(args.index_file, 'a') as indexFile:
			create_index(rootdir = rootdir,
							outfile = indexFile,
							errorfile = args.log_file,
							start_at = start_at,
							start_after = start_after,
							exclude = exclude,
							exclude_pattern = exclude_pattern,
							rel_to = args.relative_to,
							size_digits = 13,
							verbosity = args.verbose)


def prepare_collect_folders(args):
	print('collect folders')

	if args.exclude_path:
		exclude = [item for sublist in args.exclude_path for item in sublist]	#flatten list of lists
	else:
		exclude = None

	if args.exclude_pattern:
		exclude_pattern = [item for sublist in args.exclude_pattern for item in sublist]
	else:
		exclude_pattern = None

	if args.start_with:
		start_at = args.start_with
		start_after=False
	elif args.start_after:
		start_at = args.start_after
		start_after=True
	else:
		start_at = ""
		start_after=True

	for rootdir in args.rootdir:
		with open(args.collection_file, 'a') as indexFile:
			collect_folders(rootdir = rootdir,
								outfile = indexFile,
								start_at = start_at,
								start_after = start_after,
								exclude = exclude,
								exclude_pattern = exclude_pattern,
								rel_to = args.relative_to,
								fast = args.fast,
								size_digits = 7,
								verbosity = args.verbose,
								serial = args.start_serial)

def prepare_duplicate_files(args):
	print('find duplicate files')

	with open(args.duplicatelist, 'w') as duplicateList:
		find_duplicate_files(indexfiles = args.index_file,
								outfile=duplicateList,
								verbosity=args.verbose)


def prepare_similar_folders(args):
	print('find similar folders')

	with open(args.similarfolderslist, 'w') as similarFoldersList:
		find_similar_folders(indexfiles = args.index_file,
								outfile=similarFoldersList,
								verbosity=args.verbose)


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Find identical files and similar folders.')
	subparsers = parser.add_subparsers(	title='subcommands',
								description='valid subcommands:',
								help='type %(prog)s SUBCOMMAND --help for additional help')



	parser_create_index = subparsers.add_parser('createIndex',
								aliases=['ci'],
								description='walk through the given tree and store some information of each file in an index',
								help='create the Index')

	parser_create_index.add_argument('rootdir',
								nargs='+',
								help='Start indexing here. More than one dir may be given')
	parser_create_index.add_argument('index_file',
								help='file containing the index. new values will be appended')
	parser_create_index.add_argument('-v', '--verbose',
								nargs='?', const='2', default='1',
								type=int, choices=range(0,4),
								help='level of verbosity')
	parser_create_index.add_argument('-e', '--exclude-path',
								action='append',
								nargs='+',
								metavar='EXCL_PATH',
								help='exclude %(metavar)ss from index')
	parser_create_index.add_argument('-E', '--exclude-pattern',
								action='append',
								nargs='+',
								metavar='EXCL_PATTERN',
								help='exclude %(metavar)ss from index')
	start_group = parser_create_index.add_mutually_exclusive_group()
	start_group.add_argument('-s', '--start-after',
								help='start indexing after given file or folder. usefull for continuing interupted run')
	start_group.add_argument('-S', '--start-with',
								help="start indexing with given file or folder. Only either '--start-with' or '--start-after' may be given")
	parser_create_index.add_argument('-l', '--log-file')
	parser_create_index.add_argument('-R', '--relative-to',
								metavar='REL_PATH',
								help='all paths in the index file are relative to %(metavar)s')

	parser_create_index.set_defaults(func=prepare_create_index)



	parser_collect_folders = subparsers.add_parser('collectFolders',
								aliases=['cf'],
								help='create a list of all folders. This should be done when creating the index, but can be done standalone as well with this command')

	parser_collect_folders.add_argument('rootdir',
								nargs='+',
								help='Start collecting here. More than one dir may be given')
	parser_collect_folders.add_argument('collection_file',
								help='file containing the folder collection. new values will be appended')
	parser_collect_folders.add_argument('-v', '--verbose',
								nargs='?', const='2', default='1',
								type=int, choices=range(0,4),
								help='level of verbosity')
	fast_group = parser_collect_folders.add_mutually_exclusive_group()
	fast_group.add_argument('-f', '--fast',
						#		nargs=0,
								default=False,
								action='store_true',
								help="if set, don't check, if files are readable. must not occur together with -E/--exclude_pattern")
	parser_collect_folders.add_argument('-e', '--exclude-path',
								action='append',
								nargs='+',
								metavar='EXCL_PATH',
								help='exclude %(metavar)ss from index')
	fast_group.add_argument('-E', '--exclude-pattern',
								action='append',
								nargs='+',
								metavar='EXCL_PATTERN',
								help='exclude %(metavar)ss from index. must not occur together with -f/--fast')
	start_group2 = parser_collect_folders.add_mutually_exclusive_group()
	start_group2.add_argument('-s', '--start-after',
								help='start indexing after given file or folder. usefull for continuing interupted run')
	start_group2.add_argument('-S', '--start-with',
								help="start indexing with given file or folder. Only either '--start-with' or '--start-after' may be given")
	parser_collect_folders.add_argument('-R', '--relative-to',
								metavar='REL_PATH',
								help='all paths in the colltion file are relative to %(metavar)s')
	parser_collect_folders.add_argument('--start-serial',
								default = 1,
								type=int,
								metavar='START_SERIAL',
								help='start with serial at %(metavar)s. Usefull with --start-with/--start-after')
	parser_collect_folders.set_defaults(func=prepare_collect_folders)



	parser_duplicate_files = subparsers.add_parser('duplicateFiles',
								aliases=['df'],
								help='find duplicate files in the index')

	parser_duplicate_files.add_argument('index_file',
								nargs='+',
								help='file(s) to look for duplikates in. More than one file may be given')
	parser_duplicate_files.add_argument('duplicatelist',
								help='file to write the duplikates to')
	parser_duplicate_files.add_argument('-v', '--verbose',
								nargs='?', const='2', default='1',
								type=int, choices=range(0,4),
								help='level of verbosity')

	parser_duplicate_files.set_defaults(func=prepare_duplicate_files)



	parser_similar_folders = subparsers.add_parser('similarFolders',
								aliases=['sf'],
								help='find similar folders (folders that contain many duplicate files)')

	parser_similar_folders.add_argument('index_file',
								nargs='+',
								help='file(s) to look for duplikates in. More than one file may be given')
	parser_similar_folders.add_argument('similarfolderslist',
								help='file to write the findings to')
	parser_similar_folders.add_argument('-v', '--verbose',
								nargs='?', const='2', default='1',
								type=int, choices=range(0,4),
								help='level of verbosity')

	parser_similar_folders.set_defaults(func=prepare_similar_folders)



	args=parser.parse_args()
	args.func(args)
