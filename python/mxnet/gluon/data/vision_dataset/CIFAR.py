# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# coding: utf-8
# pylint: disable=
"""Dataset container."""

import os
import gzip
import tarfile
import struct
import warnings
import numpy as np

from .. import dataset
from ...utils import download, check_sha1
from .... import nd, image, recordio

from .utils import _DownloadedDataset

# TODO: add cifar 100

class CIFAR10(_DownloadedDataset):
    """CIFAR10 image classification dataset from `https://www.cs.toronto.edu/~kriz/cifar.html`_.

    Each sample is an image (in 3D NDArray) with shape (32, 32, 1).

    Parameters
    ----------
    root : str
        Path to temp folder for storing data.
    train : bool
        Whether to load the training or testing set.
    transform : function
        A user defined callback that transforms each instance. For example::

            transform=lambda data, label: (data.astype(np.float32)/255, label)
    """

    def __init__(self, root='~/.mxnet/datasets/cifar10', train=True,
                 transform=None):
        self._file_hashes = {'data_batch_1.bin': 'aadd24acce27caa71bf4b10992e9e7b2d74c2540',
                             'data_batch_2.bin': 'c0ba65cce70568cd57b4e03e9ac8d2a5367c1795',
                             'data_batch_3.bin': '1dd00a74ab1d17a6e7d73e185b69dbf31242f295',
                             'data_batch_4.bin': 'aab85764eb3584312d3c7f65fd2fd016e36a258e',
                             'data_batch_5.bin': '26e2849e66a845b7f1e4614ae70f4889ae604628',
                             'test_batch.bin': '67eb016db431130d61cd03c7ad570b013799c88c'}
        super(CIFAR10, self).__init__(root, train, transform)

    def _read_batch(self, filename):
        with open(filename, 'rb') as fin:
            data = np.fromstring(fin.read(), dtype=np.uint8).reshape(-1, 3072+1)

        return data[:, 1:].reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1), \
               data[:, 0].astype(np.int32)

    def _get_data(self):
        file_paths = [(name, os.path.join(self._root, 'cifar-10-batches-bin/', name))
                      for name in self._file_hashes]
        if any(not os.path.exists(path) or not check_sha1(path, self._file_hashes[name])
               for name, path in file_paths):
            url = 'https://www.cs.toronto.edu/~kriz/cifar-10-binary.tar.gz'
            filename = download(url, self._root,
                                sha1_hash='e8aa088b9774a44ad217101d2e2569f823d2d491')

            with tarfile.open(filename) as tar:
                tar.extractall(self._root)

        if self._train:
            filename = os.path.join(self._root, 'cifar-10-batches-bin/data_batch_%d.bin')
            data, label = zip(*[self._read_batch(filename%i) for i in range(1, 6)])
            data = np.concatenate(data)
            label = np.concatenate(label)
        else:
            filename = os.path.join(self._root, 'cifar-10-batches-bin/test_batch.bin')
            data, label = self._read_batch(filename)

        self._data = nd.array(data, dtype=data.dtype)
        self._label = label