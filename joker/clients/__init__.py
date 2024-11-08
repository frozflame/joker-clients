__version__ = "0.4.3"

from joker.clients.cas import ContentAddressedStorageClient, CascadisClient
from joker.clients.monolog import MonologInterface
from joker.clients.printable import PrintableClient

CASClient = ContentAddressedStorageClient
MonologClient = MonologInterface

if __name__ == "__main__":
    print(__version__)
