#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

from joker.clients.cas import MemberFile, ContentAddressedStorageClient
from joker.clients.utils import Pathlike

"""
Deprecated!
This module will be removed on ver 0.3.0.
"""

PathLike = Pathlike
FileStorageInterface = ContentAddressedStorageClient

__all__ = [
    "MemberFile",
    "FileStorageInterface",
]
