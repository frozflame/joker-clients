#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import os
import typing

from joker.clients.cas import MemberFile, ContentAddressedStorageClient


"""Deprecated!"""

PathLike = typing.Union[str, os.PathLike]
FileStorageInterface = ContentAddressedStorageClient

__all__ = [
    'MemberFile',
    'FileStorageInterface',
]
