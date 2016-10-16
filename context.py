# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from threading import Lock

class Context(object):
    """
    Stores data across multiple threads

    Credit: http://www.bogotobogo.com/python/Multithread/python_multithreading_Synchronization_Lock_Objects_Acquire_Release.php
    """

    def __init__(self):
        self.lock = Lock()
        self.values = {}

    def apply(self, settings={}):
        """
        Applies a block of settings
        """

        self.lock.acquire()
        try:
            for key in settings.keys():
                self.values['general.'+key] = settings[key]
        finally:
            self.lock.release()

    def get(self, key, default=None):
        """
        Retrieves the value of one key
        """

        self.lock.acquire()
        try:
            value = self.values.get(key, default)
        finally:
            self.lock.release()
            return value

    def set(self, key, value):
        """
        Remembers the value of one key
        """

        self.lock.acquire()
        try:
            self.values[key] = value
        finally:
            self.lock.release()

    def increment(self, key, delta=1):
        """
        Increments a value
        """

        self.lock.acquire()
        try:
            value = self.values.get(key, 0)
            if not isinstance(value, int):
                value = 0
            value += delta
            self.values[key] = value
        finally:
            self.lock.release()
            return value

    def decrement(self, key, delta=1):
        """
        Decrements a value
        """

        self.lock.acquire()
        try:
            value = self.values.get(key, 0)
            if not isinstance(value, int):
                value = 0
            value -= delta
            self.values[key] = value
        finally:
            self.lock.release()
            return value
