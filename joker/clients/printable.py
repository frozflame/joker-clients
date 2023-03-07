#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import json
import logging
import urllib.parse
from dataclasses import dataclass
from functools import cached_property

import requests

from joker.clients.utils import ensure_url_root

_logger = logging.getLogger(__name__)


@dataclass
class PrintableClient:
    url: str

    def __post_init__(self):
        ensure_url_root(self.url)

    @cached_property
    def session(self):
        return requests.session()

    def _post_as_json(self, url: str, data: dict):
        """
        Exists because by calling requests.post(url, json=data)
        you have nowhere to pass a parameter like default=str
        """
        headers = {'Content-type': 'application/json'}
        payload = json.dumps(data, default=str)
        return self.session.post(url, data=payload, headers=headers)

    def _generate(self, tpl_path: str, data: dict) -> (bytes, str):
        url = urllib.parse.urljoin(self.url, tpl_path)
        _logger.info('initial url: %r', url)
        resp = self._post_as_json(url, data)
        _logger.info('redirected url: %r', resp.url)
        _logger.info(
            'content: %s bytes, %r',
            len(resp.content), resp.content[:100],
        )
        if not resp.content.startswith(b'%PDF'):
            raise RuntimeError('improper header for a PDF file')
        return resp.content, resp.url

    def render_pdf(self, tpl_path: str, data: dict) -> bytes:
        assert tpl_path.endswith('.pdf')
        return self._generate(tpl_path, data)[0]

    def render_html(self, tpl_path: str, data: dict) -> str:
        assert tpl_path.endswith('.html')
        url = urllib.parse.urljoin(self.url, tpl_path)
        return self._post_as_json(url, data).text


class PDFClient(PrintableClient):
    """for backward-compatibility"""

    def __init__(self, url: str):
        super().__init__(url)

    @property
    def base_url(self):
        """for backward-compatibility"""
        return self.url

    def generate(self, tpl_path: str, data: dict) -> bytes:
        return self._generate(tpl_path, data)[0]
