#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import logging
import urllib.parse
from dataclasses import dataclass
from typing import TypedDict

from joker.clients.utils import parse_url_qsd, _HTTPClient

_logger = logging.getLogger(__name__)


class PrintableTaskDict(TypedDict):
    tpl_path: str
    ctxid: str
    html_url: str
    pdf_url: str


@dataclass
class PrintableTask:
    client: PrintableClient
    tpl_path: str
    ctxid: str

    @property
    def html_url(self):
        url = urllib.parse.urljoin(self.client.url, self.tpl_path)
        return url + f'?ctxid={self.ctxid}'

    @property
    def pdf_url(self):
        path = f'{self.tpl_path}.pdf'
        url = urllib.parse.urljoin(self.client.url, path)
        return url + f'?ctxid={self.ctxid}'

    def to_dict(self) -> PrintableTaskDict:
        return {
            'tpl_path': self.tpl_path,
            'ctxid': self.ctxid,
            'html_url': self.html_url,
            'pdf_url': self.pdf_url,
        }

    def obtain_html(self) -> str:
        return self.client.session.get(self.html_url).text

    def obtain_pdf(self) -> bytes:
        return self.client.session.get(self.pdf_url).content


class PrintableClient(_HTTPClient):
    def begin(self, tpl_path: str, data: dict) -> PrintableTask:
        assert tpl_path.endswith('.html')
        url = urllib.parse.urljoin(self.url, tpl_path)
        url += '.pdf'
        _logger.info('begin context with url: %r', url)
        resp = self._post_as_json(url, data, allow_redirects=False)
        ctxid = parse_url_qsd(resp.headers['Location'])['ctxid']
        return PrintableTask(self, tpl_path, ctxid)

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
