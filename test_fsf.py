#!/usr/bin/env python3

from fsf_core import _gethash, _get_fileinfo, _read_indexfiles, hpn

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


class test_main_path(unittest.TestCase):
	def setUp():
		pass



	pass


if __name__ == '__main__':
	unittest.main(verbosity=2)
