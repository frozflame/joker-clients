__version__ = "0.4.0"

from joker.clients.cas import ContentAddressedStorageClient
from joker.clients.monolog import MonologInterface
from joker.clients.printable import PrintableClient

CASClient = ContentAddressedStorageClient

if __name__ == "__main__":
    print(__version__)
