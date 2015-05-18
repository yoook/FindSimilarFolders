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
		child = FTree(sf)
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

	def __str__(self, level=0):
		line = "   " * level + self.name + (':\t' + str(self.cargo) if type(self.cargo)!=type(None) else "") + '\n'
		for i in self.subfolders:
			line += i.__str__(level+1)
		return line

	def __repr__(self):		#todo: care for cargo
		line = ""
		for i in self.subfolders:
			line += repr(i) + ', '
		line = line.rstrip(', ')
		if line == "" and type(self.cargo)==type(None):
			return str(self.__class__).rpartition('.')[2][:-2] + '(' + repr(self.name) +                                           ')'
		if line == "":
			return str(self.__class__).rpartition('.')[2][:-2] + '(' + repr(self.name) + ', ' + repr(self.cargo) +                 ')'
		return     str(self.__class__).rpartition('.')[2][:-2] + '(' + repr(self.name) + ', ' + repr(self.cargo) + ', [' + line + '])'


	def __getitem__(self, key):
		'if key is int, treat it as index. otherwise as name of subfolder'
		if type(key) == int:
			return self.subfolders[key]
		for i in self.subfolders:
			if i.name == key:
				return i

class FolderRefs:
	pass
