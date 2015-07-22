#!/usr/bin/env python3

from fsf_core import *
from fsf_core import _get_fileinfo, _gethash, _read_indexfiles, _collect_duplicate_files, _combine_folders_with_duplicate_files, _pair_folders_with_duplicate_files

from fsf_objects import *

import unittest
import unittest.mock as mock
import io


class test_helper_functions(unittest.TestCase):

	def test__get_fileinfo(self):
		t1 = _get_fileinfo("  124428	1413392134.8142	e800e9c562ec23614517e868799dba8e6eca9be	VMs/Win10alpha/Logs/f1")
		t2 = hpn("124428 e800e9c562ec23614517e868799dba8e6eca9be", ("VMs","Win10alpha","Logs"), "f1")
		self.assertEqual(t1, t2)


	def test__read_indexfiles(self):
		fake_file = io.StringIO("  124428	1413392134.8142	e800e9c562ec23614517e868799dba8e6eca9be	VMs/Win10alpha/Logs/f1\n  224428	1413392134.8142	e800e9c562ec23614517e868799dba8e6eca9be	VMs/Win10alpha/Logs/f1\n  324428	1413392134.8142	e800e9c562ec23614517e868799dba8e6eca9be	VMs/Win10alpha/Logs/f1\n")
		fake_file2 = io.StringIO("  424428	1413392134.8142	e800e9c562ec23614517e868799dba8e6eca9be	VMs/Win10alpha/Logs/f1\n  524428	1413392134.8142	e800e9c562ec23614517e868799dba8e6eca9be	VMs/Win10alpha/Logs/f1\n  624428	1413392134.8142	e800e9c562ec23614517e868799dba8e6eca9be	VMs/Win10alpha/Logs/f1\n")

		with mock.patch('fsf_core.open', create = True) as mockopen:
			mockopen.side_effect = [fake_file, fake_file2]
			filelist = _read_indexfiles(['foo', 'bar'], verbosity=0)
		self.assertEqual(mockopen.call_args_list, [mock.call('foo', 'r'), mock.call('bar', 'r')], "not the right files were read")
		self.assertEqual(len(filelist), 6, "not enough entries where found")
		self.assertEqual(filelist[0], hpn("124428 e800e9c562ec23614517e868799dba8e6eca9be", ("VMs","Win10alpha","Logs"), "f1"), "first entry not read correctly")
		self.assertEqual([i.hash[0] for i in filelist], ['1', '2', '3', '4', '5', '6'], "something was messed up while reading the files")

	def test__gethash(self):
		shortbytes = b"foobar"

		fake_file = io.BytesIO(shortbytes)
		with mock.patch('fsf_core.open', create = True) as mockopen:
			mockopen.return_value = fake_file
			hash = _gethash('foo')
		self.assertEqual(hash, "8843d7f92416211de9ebb963ff4ce28125932878", "wrong hash for short files")

		fake_file = io.BytesIO(shortbytes * 20000)
		with mock.patch('fsf_core.open', create = True) as mockopen:
			mockopen.return_value = fake_file
			hash = _gethash('bar')
		self.assertEqual(hash, "cfb9d945d9d322b092be7f7ae48abb9ecd618be1", "wrong hash for long files")


class test_find_similar_folders_subroutines(unittest.TestCase):
	def test__collect_duplicate_files(self):
		filelist = [
			hpn("size hash", ("folder", "with", "file", "one"), "fileone"),
			hpn("12 34", ("folder", "one"), "f1"),
			hpn("12 34", ("folder", "two"), "f2"),
			hpn("55 55", ("folder", "one"), "f3"),
			hpn("55 55", ("folder", "three"), "f3"),
			hpn("55 55", ("anotherfolder", "four"), "f4"),
			hpn("55 55", ("aanotherfolder", ), "f5"),
			hpn("55 55", ("aaan", "folder that should be", "sorted to the first", "position, but is quite long"), "f6"),
			hpn("55 55", ("aanotherfolder", ), "aaaa"), #should sort directly befor 'f5'
		]

		doublelist = [
			[(("folder", "one"), "f1"), (("folder", "two"), "f2")],
			[(("aaan", "folder that should be", "sorted to the first", "position, but is quite long"), "f6"), (("aanotherfolder", ), "aaaa"), (("aanotherfolder", ), "f5"), (("anotherfolder", "four"), "f4"), (("folder", "one"), "f3"), (("folder", "three"), "f3"),],
		]

		result = _collect_duplicate_files(filelist, verbosity=0)
		self.assertEqual(result, doublelist)

	def test__combine_folders_with_duplicate_files(self):
		doublelist = [
			[(("path1", ), "f1"), (("path2", ), "f2"), (("path3", ), "f3")],
			[(("path1", ), "f4"), (("path2", ), "f5"), (("path3", ), "f6")],

			[(("path", "10"), "f10"), (("path11",), "f11"), (("p", "a", "t", "h", "12"), "f12")]
		]

		combined = [
			[
				[("path1", ), ("path2", ), ("path3", )] ,
			 	[["f1", "f2", "f3"], ["f4", "f5", "f6"]]
			],
			[
				[("path", "10"), ("path11",), ("p", "a", "t", "h", "12")],
				[["f10", "f11", "f12"]]
			],
		]

		result = _combine_folders_with_duplicate_files(doublelist, verbosity=0)
		result.sort()
		combined.sort()
		self.assertEqual(result, combined)

	def test__pair_folders_with_duplicate_files(self):
		combined = [
			[
				[("path", "10"), ("path11",), ("p", "a", "t", "h", "12")],
				[["f10", "f11", "f12"]]
			],
			[
				[("path1",), ("path2",)],
				[["f1", "f2"]]
			],
			[
				[("p3",), ("p4",), ("p5",), ("p6",)],
				[["f3", "f4", "f5", "f6"], ["fa", "fb", "fc", "fd"]]
			],
			[
				[("p3",), ("p5",)],
				[["F3", "F5"]]
			],
		]

		paired = [
			[
				(("path", "10"), ("path11",)),
				[("f10", "f11")]
			],
			[
				(("path", "10"), ("p", "a", "t", "h", "12")),
				[("f10", "f12")]
			],
			[
				(("path11",), ("p", "a", "t", "h", "12")),
				[("f11", "f12")]
			],

			[
				(("path1",), ("path2",)),
				[("f1", "f2")]
			],

			[
				(("p3",), ("p4",)),
				[("f3", "f4"), ("fa", "fb")]
			],
			[
				(("p3",), ("p5",)),
				[("f3", "f5"), ("fa","fc"), ("F3", "F5")]
			],
			[
				(("p3",), ("p6",)),
				[("f3","f6"), ("fa", "fd")]
			],
			[
				(("p4",), ("p5",)),
				[("f4", "f5"), ("fb", "fc")]
			],
			[
				(("p4",), ("p6",)),
				[("f4","f6"), ("fb", "fd")]
			],
			[
				(("p5",), ("p6",)),
				[("f5", "f6"), ("fc", "fd")]
			],
		]

		result = _pair_folders_with_duplicate_files(combined, verbosity=0)
		result.sort()
		paired.sort()
		self.assertEqual(result, paired)


class test_fsf_objects_FTree(unittest.TestCase):
	def setUp(self):
		self.testtree = FTree("test-tree", cargo = "CARGO", subfolders=[FTree("leaf", "CARGO2"), FTree("node", subfolders=[FTree("leaf2")])])


	def test_FTree___init__(self):
		tr1 = FTree("root", None, [FTree("leaf", "CARGO1"), FTree("leaf", "CARGO2"), FTree("leaf", "CARGO3")])
		tr2 = FTree("root", None, [FTree("leaf", "CARGO3")])

		self.assertEqual(self.testtree.name, "test-tree")
		self.assertEqual(self.testtree.cargo, "CARGO")
		self.assertEqual(tr1, tr2)


	def test_FTree_append_subfolder(self):
		self.testtree.append_subfolder( FTree("new_node", 23, [FTree("new_leaf"), FTree("new_leaf2")]))
		self.testtree.append_subfolder( FTree("node", "NEW_CARGO"))

		tr = FTree("test-tree", cargo = "CARGO", subfolders=[FTree("leaf", "CARGO2"), FTree("node", "NEW_CARGO"), FTree("new_node", 23, [FTree("new_leaf"), FTree("new_leaf2")])])

		self.assertEqual(self.testtree, tr)


	def test_FTree_create_subfolder(self):
		tr1 = self.testtree.create_subfolder("new_leaf")
		tr2 = self.testtree.create_subfolder("node")

		tr = FTree("test-tree", cargo = "CARGO", subfolders=[FTree("leaf", "CARGO2"), FTree("node", subfolders=[FTree("leaf2")]), FTree("new_leaf")])

		self.assertEqual(self.testtree, tr)
		self.assertEqual(tr1, FTree("new_leaf"))
		self.assertEqual(tr2, FTree("node", subfolders=[FTree("leaf2")]))


	def test_FTree_create_branch(self):
		tr = FTree("root")
		tr1 = tr.create_branch(["node", "child", "leaf"])
		tr2 = tr.create_branch(("node", "child2"))

		self.assertEqual(tr, FTree("root", None, [FTree("node", None, [FTree("child", None, [FTree("leaf")]), FTree("child2")])]))
		self.assertEqual(tr1, FTree("leaf"))
		self.assertEqual(tr2, FTree("child2"))


	def test_FTree_remove_subfolder(self):
		tr = self.testtree.remove_subfolder("node")
		self.assertEqual(tr, FTree('node', None, [FTree('leaf2')]))
		self.assertFalse(self.testtree.remove_subfolder('node'))


	def test_FTree_get_subfolder(self):
		t1 = self.testtree.get_subfolder("leaf")
		t2 = self.testtree.get_subfolder("node")
		t3 = self.testtree.get_subfolder("node").get_subfolder("leaf2")

		self.assertEqual(t1.name, "leaf")
		self.assertEqual(t1.cargo, "CARGO2")
		self.assertEqual(t1.num_subfolders(), 0)

		self.assertEqual(t2.name, "node")
		self.assertEqual(t2.cargo, None)
		self.assertEqual(t2.num_subfolders(), 1)
		self.assertEqual(list(t2.iter_subfolders()), [FTree("leaf2")])

		self.assertEqual(t3.name, "leaf2")
		self.assertEqual(t3.cargo, None)
		self.assertEqual(t3.num_subfolders(), 0)


	def test_FTree_iter_subfolders(self):
		treelist = [FTree("node", subfolders=[FTree("leaf2")]), FTree("leaf", "CARGO2")]

		treelist1 = []
		for i in self.testtree.iter_subfolders():
			treelist1.append(i)

		self.assertEqual(len(treelist), len(treelist1))
		for i in treelist1:
			self.assertIn(i, treelist)

		for i in range(len(treelist1)):
			for j in range(len(treelist1)):
				if i==j:
					self.assertEqual(treelist1[i], treelist1[j])
				else:
					self.assertNotEqual(treelist[i], treelist[j])


	def test_FTree_num_subfolders(self):
		self.assertEqual(self.testtree.num_subfolders(), 2)
		self.assertEqual(FTree("tree2").num_subfolders(), 0)
		self.assertEqual(FTree("tree3", subfolders=[FTree("subtree", cargo=13)]).num_subfolders(), 1)


	def test_FTree_is_leaf(self):
		self.assertFalse(self.testtree.is_leaf())
		self.assertTrue( self.testtree.get_subfolder("leaf").is_leaf())
		self.assertFalse(self.testtree.get_subfolder("node").is_leaf())
		self.assertTrue(self.testtree.get_subfolder("node").get_subfolder("leaf2").is_leaf())


	def test_FTree_traverse_topdown(self):
		resultstring = ""

		def appendname(node):
			nonlocal resultstring
			resultstring += node.name + ' '

		self.testtree.traverse_topdown(appendname)
		self.assertIn(resultstring, [	"test-tree leaf node leaf2 ",
										"test-tree node leaf2 leaf", ])


	def test_FTree_traverse_bottomup(self):
		resultstring = ""

		def appendname(node):
			nonlocal resultstring
			resultstring += node.name + ' '

		self.testtree.traverse_bottomup(appendname)
		self.assertIn(resultstring, [	"leaf leaf2 node test-tree ",
										"leaf2 node leaf test-tree ", ])


	def test_FTree___eq__(self):
		tr1 = FTree("test-tree", cargo = "CARGO", subfolders=[FTree("leaf", "CARGO2"), FTree("node", subfolders=[FTree("leaf2")])])
		tr2 = FTree("test-tree", cargo = "CARGO", subfolders=[FTree("node", subfolders=[FTree("leaf2")]), FTree("leaf", "CARGO2")])
		tr3 = FTree("test-tree", cargo = "wrong", subfolders=[FTree("leaf", "CARGO2"), FTree("node", subfolders=[FTree("leaf2")])])
		tr4 = FTree("test-tree", cargo = "CARGO", subfolders=[FTree("leaf", "CARGO2"), FTree("node", subfolders=[FTree("leaf2", cargo="wrong")])])
		tr5 = FTree("test-tree", cargo = "CARGO", subfolders=[FTree("leaf", "CARGO2"), FTree("node", subfolders=[FTree("leaf2", subfolders=[FTree("wrong")])])])

		tr6 = FTree("1", None, [FTree("2", None, [FTree("5"), FTree("4")]), FTree("3")])
		tr7 = FTree("1", None, [FTree("3"), FTree("2", None, [FTree("4"), FTree("5")])])

		self.assertTrue(self.testtree == tr1)
		self.assertTrue(self.testtree == tr2)
		self.assertFalse(self.testtree == tr3)
		self.assertFalse(self.testtree == tr4)
		self.assertFalse(self.testtree == tr5)
		self.assertTrue(tr6 == tr7)


	def test_FTree___ne__(self):
		tr1 = FTree("test-tree", cargo = "CARGO", subfolders=[FTree("leaf", "CARGO2"), FTree("node", subfolders=[FTree("leaf2")])])
		tr2 = FTree("test-tree", cargo = "CARGO", subfolders=[FTree("node", subfolders=[FTree("leaf2")]), FTree("leaf", "CARGO2")])
		tr3 = FTree("test-tree", cargo = "wrong", subfolders=[FTree("leaf", "CARGO2"), FTree("node", subfolders=[FTree("leaf2")])])
		tr4 = FTree("test-tree", cargo = "CARGO", subfolders=[FTree("leaf", "CARGO2"), FTree("node", subfolders=[FTree("leaf2", cargo="wrong")])])
		tr5 = FTree("test-tree", cargo = "CARGO", subfolders=[FTree("leaf", "CARGO2"), FTree("node", subfolders=[FTree("leaf2", subfolders=[FTree("wrong")])])])

		tr6 = FTree("1", None, [FTree("2", None, [FTree("5"), FTree("4")]), FTree("3")])
		tr7 = FTree("1", None, [FTree("3"), FTree("2", None, [FTree("4"), FTree("5")])])

		self.assertFalse(self.testtree != tr1)
		self.assertFalse(self.testtree != tr2)
		self.assertTrue(self.testtree != tr3)
		self.assertTrue(self.testtree != tr4)
		self.assertTrue(self.testtree != tr5)
		self.assertFalse(tr6 != tr7)


	def test_FTree___str__(self):
		self.assertIn(self.testtree.__str__(), [ 	"test-tree:\tCARGO\n   leaf:\tCARGO2\n   node\n      leaf2\n",
		 											"test-tree:\tCARGO\n   node\n      leaf2\n   leaf:\tCARGO2\n"  ])


	def test_FTree___repr__(self):
		self.assertIn(self.testtree.__repr__(), [	"FTree('test-tree', 'CARGO', [FTree('leaf', 'CARGO2'), FTree('node', None, [FTree('leaf2')])])",
													"FTree('test-tree', 'CARGO', [FTree('node', None, [FTree('leaf2')]), FTree('leaf', 'CARGO2')])"  ])


class test_fsf_opjects_FolderRefs(unittest.TestCase):
	def setUp(self):
		self.testfolderref = FolderRefs(3, 5, {"a": 3, "b": 6}, {"c": 9, "d": 0})


	def test_FolderRefs___init__(self):
		self.assertEqual(self.testfolderref.nfiles, 3)
		self.assertEqual(self.testfolderref.nsubfolders, 5)
		self.assertEqual(self.testfolderref.file_dups, Counter({"a": 3, "b": 6}))
		self.assertEqual(self.testfolderref.subfolder_dups, Counter({"c": 9, "d": 0}))
		self.assertEqual(self.testfolderref.hidden_file_dups, Counter({}))
		self.assertEqual(self.testfolderref.hidden_subfolder_dups, Counter({}))


	def test_FolderRefs___str__(self):
		self.assertIn(self.testfolderref.__str__(), [	"3, 5, {'a': 3, 'b': 6}, {'c': 9, 'd': 0}",
														"3, 5, {'a': 3, 'b': 6}, {'d': 0, 'c': 9}",
														"3, 5, {'b': 6, 'a': 3}, {'c': 9, 'd': 0}",
														"3, 5, {'b': 6, 'a': 3}, {'d': 0, 'c': 9}"  ])


	def test_FolderRefs___repr__(self):
		self.assertIn(self.testfolderref.__repr__(), [	"FolderRefs(3, 5, {'a': 3, 'b': 6}, {'c': 9, 'd': 0})",
														"FolderRefs(3, 5, {'a': 3, 'b': 6}, {'d': 0, 'c': 9})",
														"FolderRefs(3, 5, {'b': 6, 'a': 3}, {'c': 9, 'd': 0})",
														"FolderRefs(3, 5, {'b': 6, 'a': 3}, {'d': 0, 'c': 9})"  ])


if __name__ == '__main__':
	unittest.main(verbosity=2)
