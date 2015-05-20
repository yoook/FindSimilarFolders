from collections import Counter

class FTree(object):
	'Tree object'
	def __init__(self, name, cargo=None, subfolders=None):
		self.name = name
		self.cargo = cargo
		self.subfolders = [] if subfolders is None else subfolders


	def create_subfolder(self, sf):
		'create a subfolder of given name and return it'
		for i in self.subfolders:
			if i.name == sf:
				return i
		child = self.__new__(type(self))
		child.__init__(sf)
		self.subfolders.append(child)
		return child

	def create_subtree(self, st):
		'create a complete branch out of a given tuple or list of names of nodes. return the last subfolder'
		if st:
			for i in self.subfolders:
				if i.name == st[0]:
					return i.create_subtree(st[1:])
			self.create_subfolder(st[0])
			return self[st[0]].create_subtree(st[1:])
		else:
			return self

	def append_subfolder(self, sf):
		'append the given folder as subfolder'
		self.subfolders.append(sf)

	def traverse_topdown(self, function):
		'traverse this tree topdown. apply functionto each node. so function has to take exactly one node element as argument'
		function(self)

		for i in self.subfolders:
			i.traverse_topdown(function)


	def traverse_bottomup(self, function):
		'traverse this tree bottomup. apply functionto each node. so function has to take exactly one node element as argument'
		for i in self.subfolders:
			i.traverse_bottomup(function)

		function(self)


	def __str__(self, level=0):
		line = "   " * level + self.name + (':\t' + str(self.cargo) if type(self.cargo)!=type(None) else "") + '\n'
		for i in self.subfolders:
			line += i.__str__(level+1)
		return line

	def __repr__(self):
		line = repr(self.subfolders)
		if line == "[]" and type(self.cargo)==type(None):
			return self.__class__.__name__ + '(' + repr(self.name) +                                         ')'
		if line == "[]":
			return self.__class__.__name__ + '(' + repr(self.name) + ', ' + repr(self.cargo) +               ')'
#		if type(self.cargo)==type(None): 	# if cargo==None-> print extra version with subfolders as positional argument. longer, but less confusing
#			return self.__class__.__name__ + '(' + repr(self.name) + ', ' +           'subfolders=' + line + ')'
		return     self.__class__.__name__ + '(' + repr(self.name) + ', ' + repr(self.cargo) + ', ' + line + ')'


	def __getitem__(self, key):
		'if key is int, treat it as index. otherwise as name of subfolder'
		if type(key) == int:
			return self.subfolders[key]
		for i in self.subfolders:
			if i.name == key:
				return i

class FolderRefs:
	def __init__(self, nfiles=0, nsubfolders=0, folder_with_dup_files=None):
		self.nfiles = nfiles
		self.nsubfolders = nsubfolders
		self.folder_with_dup_files = Counter({}) if folder_with_dup_files is None else folder_with_dup_files


	def __str__(self):
		return str(self.nfiles) + ', ' + str(self.nsubfolders) + ', ' + str(self.folder_with_dup_files)

	def __repr__(self):
		return self.__class__.__name__ + '(' + repr(self.nfiles)+ ', ' + repr(self.nsubfolders) + ', ' + repr(self.folder_with_dup_files) + ')'

	pass


class FTreeStat(FTree):
	def __init__(self, name):
		#super().__init__(name, cargo=FolderRefs()) 	# this works only with Python 3
		super(type(self), self).__init__(name, cargo=FolderRefs(), subfolders = [])		# for compatibility with python 2

	def add_count(self, filefolder, dups):
		'take an entry of the filelist and one matching of the filedict and update the FTreeStat'

		if filefolder.path[-1] != self.name:		# error! This tree node does not belong to the given filefolder entry!
			return 0
		self.cargo.nfiles += 1
		self.cargo.folder_with_dup_files.update(dict(dups).keys())	# dict(dups).keys: reduce the number of files countet per folder to one

	def remove_unimportant(self):
		'this function shall remove folders from the counter, that are not "similar enough". overwrite it with something suitable'
		for i in self.cargo.folder_with_dup_files.copy():
			if self.cargo.folder_with_dup_files[i] < self.cargo.nfiles - 2:	# if more than two files are missing -> delete
				del self.cargo.folder_with_dup_files[i]

