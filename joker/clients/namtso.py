#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

from urllib.parse import urljoin

import requests


class _NamtsoClient:
    def __init__(self, base_url: str):
        self.base_url = base_url


class NamtsoResolverClient(_NamtsoClient):
    def acquire(self, kind: str):
        url = urljoin(self.base_url, "acquire")
        resp = requests.post(url, json={"kind": kind})
        return resp.json()["data"]

    def release(self, vtid: str, output: dict):
        url = urljoin(self.base_url, "release")
        resp = requests.post(url, json={"vtid": vtid, "output": output})
        return resp.json()["data"]


class NamtsoInquirerClient(_NamtsoClient):
    def publish(self, kind: str, input_: dict) -> str:
        url = urljoin(self.base_url, "publish")
        resp = requests.post(url, json={"kind": kind, "input": input_})
        return resp.json()["data"]

    def inquire(self, vtid: str, timeout: int | float = 0):
        url = urljoin(self.base_url, "inquire")
        resp = requests.post(url, json={"vtid": vtid, "timeout": timeout})
        return resp.json()["data"]
