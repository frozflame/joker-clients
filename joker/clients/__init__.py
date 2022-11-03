__version__ = '0.1.1'

from joker.clients.monolog import MonologInterface
from joker.clients.printable import PDFClient
from joker.clients.storage import FileStorageInterface

if __name__ == '__main__':
    print(__version__)
