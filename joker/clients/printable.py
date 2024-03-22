#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import cached_property
from typing import TypedDict
from urllib.parse import urljoin

import requests
from volkanic.errors import TechnicalError

from joker.clients import utils

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

    def _fmt_url(self, base: str, path: str) -> str:
        url = urljoin(base, path)
        return url + f"?ctxid={self.ctxid}"

    @property
    def inner_html_url(self) -> str:
        return self._fmt_url(self.client.inner_url, self.tpl_path)

    @property
    def inner_pdf_url(self) -> str:
        return self._fmt_url(self.client.inner_url, f"{self.tpl_path}.pdf")

    @property
    def outer_html_url(self) -> str:
        return self._fmt_url(self.client.outer_url, self.tpl_path)

    @property
    def outer_pdf_url(self) -> str:
        return self._fmt_url(self.client.outer_url, f"{self.tpl_path}.pdf")

    def to_dict(self) -> PrintableTaskDict:
        return {
            "tpl_path": self.tpl_path,
            "ctxid": self.ctxid,
            "html_url": self.outer_html_url,
            "pdf_url": self.outer_pdf_url,
        }

    def obtain_html(self) -> str:
        return self.client.session.get(self.inner_html_url).text

    def obtain_pdf(self) -> bytes:
        return self.client.session.get(self.inner_pdf_url).content


@dataclass
class PrintableClient:
    inner_url: str
    outer_url: str = None

    @classmethod
    def from_cfg(cls, cfg: str | dict):
        if isinstance(cfg, str):
            return cls(cfg)
        return cls(**cfg)

    @cached_property
    def session(self):
        return requests.session()

    def __post_init__(self):
        utils.ensure_url_root(self.inner_url)
        if self.outer_url is None:
            self.outer_url = self.inner_url
        c = self.__class__.__name__
        _logger.info("new %s instance, %r", c, self.inner_url)

    @staticmethod
    def _post_as_json(url, data, allow_redirects=False) -> requests.Response:
        resp = utils.post_as_json(url, data, allow_redirects=allow_redirects)
        status = resp.status_code
        if status >= 400:
            raise TechnicalError(f"got response status code {status}")
        return resp

    def begin(self, tpl_path: str, data: dict) -> PrintableTask:
        assert tpl_path.endswith(".html")
        url = urljoin(self.inner_url, tpl_path)
        url += ".pdf"
        _logger.info("begin context with url: %r", url)
        resp = self._post_as_json(url, data, allow_redirects=False)
        try:
            ctxid = utils.parse_url_qsd(resp.headers["Location"])["ctxid"]
        except KeyError:
            raise RuntimeError(f"failed to render {url!r}")
        return PrintableTask(self, tpl_path, ctxid)

    def _generate(self, tpl_path: str, data: dict) -> tuple[bytes, str]:
        url = urljoin(self.inner_url, tpl_path)
        _logger.info("initial url: %r", url)
        resp = self._post_as_json(url, data)
        _logger.info("redirected url: %r", resp.url)
        _logger.info(
            "content: %s bytes, %r",
            len(resp.content),
            resp.content[:100],
        )
        if not utils.check_pdf_validity(resp.content):
            raise RuntimeError("corrupted PDF file")
        return resp.content, resp.url

    def render_pdf(self, tpl_path: str, data: dict) -> bytes:
        assert tpl_path.endswith(".pdf")
        return self._generate(tpl_path, data)[0]

    def render_html(self, tpl_path: str, data: dict) -> str:
        assert tpl_path.endswith(".html")
        url = urljoin(self.inner_url, tpl_path)
        return self._post_as_json(url, data).text

    @property
    def base_url(self):
        """for backward-compatibility"""
        return self.inner_url
