from collections import Counter

class FTree(object):
	'''Tree object'''
	def __init__(self, name, cargo=None, subfolders=None):
		self.name = name
		self.cargo = cargo

		# _subfolders shall be accessed ONLY by
		# append_subfolder(), remove_subfolder(), iter_subfolders(),
		# num_subfolders, __eq__(), traverse_topdown() and traverse_bottomup()
		self._subfolders = []
		if subfolders:
			for i in subfolders:
				self.append_subfolder(i)

		#_parent shall be accessed ONLY by append_subfolder() and get_parent()
		self._parent = None


	def append_subfolder(self, sf):
		'''append the given folder as subfolder.
		If a subfolder of the same name as 'sf' already exists, overwrite it
		type(sf) == FTree!'''

		if sf.name in [i.name for i in self._subfolders]: # does a subfolder of this
			self.remove_subfolder(sf.name)				  # name already exist?

		sf._parent = self
		self._subfolders.append(sf)


	def create_subfolder(self, sfName):
		'''create a subfolder of given name and return it.
		if it already exists, just return it.
		type(sf) == str, not FTree!'''

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
		return the last subfolder. if it already exists, just return it.
		so you can use this to get an arbitrary node from the middle of the tree!
		type(subtreeNames) == tuple or list
		type(subtreeNames[i]) == str'''

		if subtreeNames:
			return self.create_subfolder(subtreeNames[0]).create_branch(subtreeNames[1:])
		else:
			return self


	def remove_subfolder(self, sfName):
		''' remove the subfolder of the given name from this tree and return
		this subfolder.
		return False, if there was no subfolder of given name'''

		for i in range(self.num_subfolders()):
			if self._subfolders[i].name == sfName:
				return self._subfolders.pop(i)
		return False


	def get_subfolder(self, sfName):
		'''return subfolder of given name. If not available, return NONE'''

		for i in self.iter_subfolders():
			if i.name == sfName:
				return i
		return None


	def get_by_path(self, path):
		'''return the subfolder, given by
		a path relative to self.
		path is a tuple or a list of names.
		If not available, return NONE'''

		if not path:
			return self
		if not path[0] in self:
			return None
		return self.get_subfolder(path[0]).get_by_path(path[1:])


	def iter_subfolders(self):
		'''return subfolders one by one'''

		for i in self._subfolders:
			yield i


	def num_subfolders(self):
		'''return number of subfolders'''

		return len(self._subfolders)	# less elegance, but better performance
		#return len(list(self.iter_subfolders()))


	def get_parent(self):
		'''return the parent node.
		when called on the root node, return None'''

		return self._parent


	def is_leaf(self):
		return self.num_subfolders() == 0


	def traverse_topdown(self, function):
		'''traverse this tree topdown. apply function to each node.
		so function has to take exactly one node element as argument'''

		function(self)

		for i in reversed(self._subfolders): # reversed avoids problems, when
											 # removing nodes while traversing
			i.traverse_topdown(function)


	def traverse_bottomup(self, function):
		'''traverse this tree bottomup. apply function to each node.
		so function has to take exactly one node element as argument'''

		for i in reversed(self._subfolders):
			i.traverse_bottomup(function)

		function(self)


	def __eq__(self, other):
		'''compare for equality. Do not care about the _parent!
		side effect: sort the list '_subfolders' of this and the other tree!
		automatically descands into children and sorts ALL '_subfolders' of all descandants!'''

		if type(self) == type(other):

			if self.name == other.name and self.cargo == other.cargo:
				self._subfolders.sort(key=lambda x:x.name)
				other._subfolders.sort(key=lambda x:x.name)
				if self._subfolders == other._subfolders:
					return True

			return False

		return NotImplemented


	def __ne__(self, other):
		'''compare for not equal'''

		return not self == other


	def __contains__(self, sfName):
		'''test, if there is a subfolder of the given name'''
		for i in self.iter_subfolders():
			if i.name == sfName:
				return True

		return False


	def __str__(self, level=0):
		'''produce a nice string showing the structure (and more or less the content) of this tree'''

		line = "   " * level + self.name + (':\t' + str(self.cargo) if type(self.cargo)!=type(None) else "") + '\n'
		for i in self.iter_subfolders():
			line += i.__str__(level+1)
		return line


	def __repr__(self):
		'''produce a string that would generate this tree if pasted to the python console'''

		line = repr(list(self.iter_subfolders()))
		if line == "[]" and type(self.cargo)==type(None):
			return self.__class__.__name__ + '(' + repr(self.name) +                                         ')'
		if line == "[]":
			return self.__class__.__name__ + '(' + repr(self.name) + ', ' + repr(self.cargo) +               ')'
		return     self.__class__.__name__ + '(' + repr(self.name) + ', ' + repr(self.cargo) + ', ' + line + ')'


# untested
class hpn(object):
	'''replaces namedtuple HashPathName and extends it
	by the size. Tries to reconstruct the size from the hash,
	if not given, but should always be instanciated with a given
	size, so that it can later be replaced by a namedtuple again for
	performance reasons. __eq__ and __ne__ are only used in tests'''

	def __init__(self, hash, path, name, size=None):
		self.hash = hash
		self.path = path
		self.filename = name

		if size != None:
			self.size = size
		else:
			try:
				self.size = int(self.hash.split(' ')[0].strip())
			except ValueError:
				self.size = 0


	def __getitem__(self, index):
		'''allow access by index. Slice-Syntax is not supported'''

		if index==0: return self.hash
		if index==1: return self.path
		if index==2: return self.filename
		if index==3: return self.size
		raise IndexError

	def __eq__(self, other):
		'''compare for equality'''

		if type(self) == type(other):
			return self.__dict__ == other.__dict__
		return NotImplemented


	def __ne__(self, other):
		'''compare for not equal'''

		return not self == other

# untested
class Cargo(object):
	'''this class is meant to be used by dynamically adding
	whatever attribute is needed'''

	def __str__(self, level=0):
		'''used only for printf-debuging. return whatever you want to know'''
		space = "   " * level
		line = ""
		for k, v in self.__dict__.items():
			line += str(k) + ": " + str(v) + "\n" + space
		return line

	def __eq__(self, other):
		'''compare for equality'''

		if type(self) == type(other):
			return self.__dict__ == other.__dict__
		return NotImplemented


	def __ne__(self, other):
		'''compare for not equal'''

		return not self == other


class FTreeStat(FTree):
	def __init__(self, name, subfolders=None, **kwargs):
		'''kwargs are added to cargo as attributes'''

		cargo = Cargo()
		cargo.hashdict = {}	# this dict will carry all hashes of files in this
							# Folder as keys and the filesize as values
		cargo.dup_candidates = set() # these folders MIGHT BE dups
		cargo.dup_confirmed = set()  # these folders ARE CONFIRMED dups
		# cargo.unique = False #uniques are just deleted. no need to store that information
		cargo.num_subfolders = 0
		cargo.num_f_subfolders = 0
		cargo.size_subfolders = 0
		for key, value in kwargs.items():
			cargo.__dict__[key] = value

		super().__init__(name, cargo, subfolders)

	def __str__(self, level=0):
		'''produce a nice string showing the structure (and more or less the content) of this tree'''

		line = "   " * level \
		 		+ self.name \
				+ ':\t' \
				+ self.cargo.__str__(level+2) if type(self.cargo)!=type(None) else "" \
				+ '\n'
		for i in self.iter_subfolders():
			line += i.__str__(level+1)
		return line


	def add_hash(self, hash, size, paths):
		''' add the given hash to the dictionary of hashes in this node and
		the size as key.
		add the path to the set of dup_candidates of this node'''

		self.cargo.hashdict[hash] = size
		self.cargo.dup_candidates.update(paths)


	def collect_stats_remove_uniques(self):
		'''collect statistic information about the node and propagate it to
		the parents. remove nodes, that are completely unique, as they are not
		needed any more'''

		if not self.get_parent():
			return	# for the root node do nothing

		size_f_this = sum(self.cargo.hashdict.values())
		num_f_this = len(self.cargo.hashdict)
		self.get_parent().cargo.num_subfolders += 1
		self.get_parent().cargo.num_f_subfolders += self.cargo.num_f_subfolders + num_f_this
		self.get_parent().cargo.size_subfolders  += self.cargo.size_subfolders + size_f_this

		if self.is_leaf() and len(self.cargo.dup_candidates) <= 1:	# i.e. dup only with itsself
			# this node is removed anyway. no need to store anything
			# self.cargo.unique = True
			self.get_parent().remove_subfolder(self.name) # remove this node


#	def __del__(self):
#		'''for printf-debuging only'''
#		print("removing ", self.name)
