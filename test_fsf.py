#!/usr/bin/env python3

from fsf_core import *
from fsf_core import _get_fileinfo, _gethash, _read_indexfiles, _collect_duplicate_files, _combine_folders_with_duplicate_files, _pair_folders_with_duplicate_files

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



if __name__ == '__main__':
	unittest.main(verbosity=2)
