# Copyright 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for fastq_reader CLIF python wrappers."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function



from absl.testing import absltest

from nucleus.io import clif_postproc
from nucleus.io.python import fastq_reader
from nucleus.protos import fastq_pb2
from nucleus.testing import test_utils


class FastqReaderTest(absltest.TestCase):

  def setUp(self):
    self.fastq = test_utils.genomics_core_testdata('test_reads.fastq')
    self.zipped_fastq = test_utils.genomics_core_testdata('test_reads.fastq.gz')
    self.options = fastq_pb2.FastqReaderOptions()

  def test_fastq_iterate(self):
    with fastq_reader.FastqReader.from_file(self.fastq, self.options) as reader:
      iterable = reader.iterate()
      self.assertIsInstance(iterable, clif_postproc.WrappedCppIterable)
      self.assertEqual(test_utils.iterable_len(iterable), 3)

    zreader = fastq_reader.FastqReader.from_file(
        self.zipped_fastq,
        fastq_pb2.FastqReaderOptions(
            compression_type=fastq_pb2.FastqReaderOptions.GZIP))
    with zreader:
      ziterable = zreader.iterate()
      self.assertIsInstance(ziterable, clif_postproc.WrappedCppIterable)
      self.assertEqual(test_utils.iterable_len(ziterable), 3)

  def test_from_file_raises_with_missing_fastq(self):
    with self.assertRaisesRegexp(ValueError,
                                 'Not found: Could not open missing.fastq'):
      fastq_reader.FastqReader.from_file('missing.fastq', self.options)

  def test_ops_on_closed_reader_raise(self):
    reader = fastq_reader.FastqReader.from_file(self.fastq, self.options)
    with reader:
      pass
    # At this point the reader is closed.
    with self.assertRaisesRegexp(ValueError, 'Cannot Iterate a closed'):
      reader.iterate()

  def test_fastq_iterate_raises_on_malformed_record(self):
    malformed = test_utils.genomics_core_testdata('malformed.fastq')
    reader = fastq_reader.FastqReader.from_file(malformed, self.options)
    iterable = iter(reader.iterate())
    self.assertIsNotNone(next(iterable))
    with self.assertRaises(ValueError):
      list(iterable)


if __name__ == '__main__':
  absltest.main()
