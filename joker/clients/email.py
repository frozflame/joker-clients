#!/usr/bin/env python3
# coding: utf-8

import logging
import mimetypes
import os.path
import smtplib
import socket
from dataclasses import dataclass
from email import encoders
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import cached_property
from typing import TypedDict
from typing import Union, List

_logger = logging.getLogger(__name__)


class ExtendedEmailMessage(EmailMessage):
    @staticmethod
    def _fmt_addrs(addrs: Union[List[str], str], sep=", "):
        if isinstance(addrs, str):
            return addrs
        return sep.join(addrs)

    def set_subject_and_addrs(
        self,
        subject: str,
        from_addr: str,
        to_addrs: Union[List[str], str],
        cc_addrs: Union[List[str], str] = None,
    ):
        self["Subject"] = subject
        self["From"] = from_addr
        self["To"] = self._fmt_addrs(to_addrs)
        if cc_addrs:
            self["Cc"] = self._fmt_addrs(cc_addrs)

    def add_attachment_from_local_file(self, path: str):
        mime = mimetypes.guess_type(path)[0]
        maintype, subtype = mime.split("/", 1)
        filename = os.path.split(path)[1]
        with open(path, "rb") as fin:
            content = fin.read()
            self.add_attachment(
                content,
                filename=filename,
                maintype=maintype,
                subtype=subtype,
            )


# deprecated; will be removed at ver 0.5.0
class EmailInterface:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        from_addr: str,
        fake=False,
    ):
        """
        Args:
            host:
            port:
            username:
            password:
            from_addr:
            fake: if true, messages will NOT be send actually
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.fake = fake

    def _get_smtp(self):
        smtp = smtplib.SMTP(self.host, self.port)
        smtp.login(self.username, self.password)
        return smtp

    def _send(self, from_addr, to_addrs, msg):
        smtp = self._get_smtp()
        try:
            resp = smtp.sendmail(from_addr, to_addrs, msg)
            _logger.info("smtp.sendmail() => %s", resp)
        finally:
            smtp.quit()
            _logger.info("smtp.quit()")
        return resp

    def send(
        self,
        subject: str,
        content: str,
        attachments: list,
        from_addr: Union[str, None],
        to_addrs: Union[List[str], str],
        cc_addrs: Union[List[str], str] = None,
        content_subtype="html",
    ):
        """
        Args:
            subject:
            content:
            attachments
            from_addr: override default from_addr
            to_addrs:
            cc_addrs:
            content_subtype:
        """
        from_addr = from_addr or self.from_addr
        mail = ExtendedEmailMessage()
        mail.set_subject_and_addrs(
            subject,
            from_addr,
            to_addrs,
            cc_addrs,
        )
        mail.set_content(content, subtype=content_subtype)
        for att in attachments:
            mail.add_attachment_from_local_file(att)

        msg = mail.as_string()
        _logger.debug("EmailMessage().as_string()[:100] => %s", msg[:100])
        _logger.info("EmailMessage().fake => %s", self.fake)
        if not self.fake:
            return self._send(from_addr, to_addrs, msg)


class EmailAccount(TypedDict):
    user: str
    password: str


class EmailAgentConfDict(TypedDict):
    host: str
    port: int
    accounts: list[EmailAccount]


@dataclass
class EmailAgent:
    host: str
    port: int
    accounts: list[EmailAccount]

    @cached_property
    def _local_hostname(self) -> str:
        return socket.getfqdn()

    def _look_for_account(self, user: str) -> EmailAccount:
        for account in self.accounts:
            if account["user"] == user:
                return account
        raise LookupError(f"email account {user} not found")

    def login(self, user: str):
        smtp = smtplib.SMTP(
            self.host,
            self.port,
            local_hostname=self._local_hostname,
        )
        account = self._look_for_account(user)
        smtp.login(**account)
        return smtp

    def send(
        self,
        from_addr: str,
        to_addrs: list,
        subject: str,
        body: str | MIMEBase,
        attachments: list[MIMEBase] = None,
    ):
        """
        Note:
            SMTP.send_message() is a convenience method for calling SMTP.sendmail()
            with the message represented by an email.message.Message object.
            https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.send_message
        """
        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["To"] = ", ".join(to_addrs)
        msg["Subject"] = subject
        if isinstance(body, str):
            body = MIMEText(body, "plain")
        msg.attach(body)
        attachments = attachments or []
        for attachment in attachments:
            msg.attach(attachment)
        with self.login(from_addr) as smtp:
            # If from_addr is None or to_addrs is None, send_message() fills
            # those arguments with addresses extracted from the headers of
            # msg as specified in RFC 5322.
            smtp.send_message(msg)
            # alternatively, one can use:
            # smtp.sendmail(from_addr, to_addrs, msg.as_string())

    @staticmethod
    def create_attachment(content: bytes, filename: str) -> MIMEBase:
        maintype, subtype = mimetypes.guess_type(filename)[0].split("/")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(content)
        # why encode in base64?
        # https://stackoverflow.com/a/76324353/2925169
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename=("utf-8", "", filename),
        )
        return attachment
