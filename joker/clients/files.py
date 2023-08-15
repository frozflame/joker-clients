#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import os
import typing

from joker.clients.cas import MemberFile, ContentAddressedStorageClient

"""
Deprecated!
This module will be removed on ver 0.3.0.
"""

PathLike = typing.Union[str, os.PathLike]
FileStorageInterface = ContentAddressedStorageClient

__all__ = [
    'MemberFile',
    'FileStorageInterface',
]
