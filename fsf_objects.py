from collections import Counter

class FTree(object):
	'''Tree object'''
	def __init__(self, name, cargo=None, subfolders=None):
		self.name = name
		self.cargo = cargo

		# _subfolders shall be accessed ONLY by append_subfolder(), remove_subfolder, iter_subfolders(), num_subfolders and __eq__()
		self._subfolders = []
		if subfolders:
			for i in subfolders:
				self.append_subfolder(i)


	def append_subfolder(self, sf):
		'''append the given folder as subfolder.
		If a subfolder of the same name as 'sf' already exists, overwrite it
		type(sf) == FTree!
		'''

		if sf.name in [i.name for i in self._subfolders]:
			self.remove_subfolder(sf.name)
		self._subfolders.append(sf)


	def remove_subfolder(self, sfName):
		''' remove the subfolder of the given name from this tree and return
		this subfolder.
		return False, if there was no subfolder of given name'''

		for i in range(self.num_subfolders()):
			if self._subfolders[i].name == sfName:
				return self._subfolders.pop(i)
		return False


	def create_subfolder(self, sfName):
		'''create a subfolder of given name and return it
		if it already exists, just return it
		type(sf) == str, not FTree!
		'''

		tmp = self.get_subfolder(sfName)
		if tmp:
			return tmp

		child = self.__new__(type(self))
		child.__init__(sfName)
		self.append_subfolder(child)
		return child


	def create_branch(self, subtreeNames):
		'''create a complete branch out of a given tuple or list of names of nodes.
		no bifurcations possible!
		return the last subfolder
		type(subtreeNames) == tuple or list
		type(subtreeNames[i]) == str'''

		if subtreeNames:
			return self.create_subfolder(subtreeNames[0]).create_branch(subtreeNames[1:])
		else:
			return self


	def is_leaf(self):
		return self.num_subfolders() == 0


	def traverse_topdown(self, function):
		'traverse this tree topdown. apply function to each node. so function has to take exactly one node element as argument'
		function(self)

		for i in self.iter_subfolders():
			i.traverse_topdown(function)


	def traverse_bottomup(self, function):
		'traverse this tree bottomup. apply function to each node. so function has to take exactly one node element as argument'
		for i in self.iter_subfolders():
			i.traverse_bottomup(function)

		function(self)


	def __eq__(self, other):
		'''compare for equality
		side effect: sort the list '_subfolders' of this and the other tree!
		automatically descands into children and sorts ALL '_subfolders' of all descandants!
		'''
		if type(self) == type(other):
			self._subfolders.sort(key=lambda x:x.name)
			other._subfolders.sort(key=lambda x:x.name)
			return self.__dict__ == other.__dict__
		return NotImplemented


	def __ne__(self, other):
		'''compare for not equal'''
		return not self == other


	def __str__(self, level=0):
		line = "   " * level + self.name + (':\t' + str(self.cargo) if type(self.cargo)!=type(None) else "") + '\n'
		for i in self.iter_subfolders():
			line += i.__str__(level+1)
		return line


	def __repr__(self):
		line = repr(list(self.iter_subfolders()))
		if line == "[]" and type(self.cargo)==type(None):
			return self.__class__.__name__ + '(' + repr(self.name) +                                         ')'
		if line == "[]":
			return self.__class__.__name__ + '(' + repr(self.name) + ', ' + repr(self.cargo) +               ')'
		return     self.__class__.__name__ + '(' + repr(self.name) + ', ' + repr(self.cargo) + ', ' + line + ')'


	def get_subfolder(self, sfName):
		'''return subfolder of given name. If not available, return NONE'''

		for i in self.iter_subfolders():
			if i.name == sfName:
				return i
		return None


	def iter_subfolders(self):
		'''return subfolders one by one'''

		for i in self._subfolders:
			yield i


	def num_subfolders(self):
		'''return number of subfolders'''

		return len(self._subfolders)	# less elegance, but better performance
		#return len(list(self.iter_subfolders()))


class FolderRefs:
	def __init__(self, nfiles=0, nsubfolders=0, file_dups=None, subfolder_dups=None):
		self.nfiles = nfiles
		self.nsubfolders = nsubfolders

		self.file_dups = Counter({}) if file_dups is None else file_dups
		self.subfolder_dups = Counter({}) if subfolder_dups is None else subfolder_dups

		self.hidden_file_dups = Counter({})				# keep already counted and collected files and subfolders here for future reference
		self.hidden_subfolder_dups = Counter({})

	def __str__(self):
		return str(self.nfiles) + ', ' + str(self.nsubfolders) + ', ' + str(self.file_dups) + ', ' + str(self.subfolder_dups)

	def __repr__(self):
		return self.__class__.__name__ + '(' + repr(self.nfiles)+ ', ' + repr(self.nsubfolders) + ', ' + repr(self.file_dups) + ', ' + repr(self.subfolder_dups) + ')'


class FTreeStat(FTree):
	def __init__(self, name, cargo=None, subfolders=None):
		if not cargo:
			cargo = FolderRefs()
		super().__init__(name, cargo, subfolders=subfolders) 	# this works only with Python 3
		#super(type(self), self).__init__(name, cargo, subfolders=subfolders)		# for compatibility with python 2

	def add_count(self, dups):
		'take an entry the filedict and update the FTreeStat'

		self.cargo.nfiles += 1
		self.cargo.file_dups.update(dict(dups).keys())	# dict(dups).keys: reduce the number of files counted per folder to one

	def remove_unsimilar(self):
		'this function shall remove folders from the counter, that are not "similar enough". overwrite it with something suitable'
		if self.cargo.nfiles <=1:
			self.cargo.file_dups = Counter()			# remove everything (replacing with new, empty counter).

		l = self.cargo.file_dups.copy().keys()
		for i in l:
			if i == self.get_path()[1:]:								# obviously each folder is identical to itsself. don't count that.
				del self.cargo.file_dups[i]
				continue

			if self.cargo.file_dups[i] < self.cargo.nfiles - 2:	# if more than two files are missing -> delete
				del self.cargo.file_dups[i]
				continue

	#def collect(self):		# todo: give better name
	#	for i in self.subfolders:
	#		self.cargo.subfolder_dups.update(dict(i.cargo.


	def ____str__(self, level=0):							# todo: for testing only. remove later, so the parent __str__ is used
		line = "   " * level + self.name + ':\t' + str(self.cargo.nfiles) + ': ' + str(len(self.cargo.file_dups)) + '\n'
		for i in self.subfolders:
			line += i.__str__(level+1)
		return line
