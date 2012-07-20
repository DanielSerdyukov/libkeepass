# -*- coding: utf-8 -*-
import io
from contextlib import contextmanager

from common import read_signature
from kdb3 import KDB3Reader
from kdb4 import KDB4Reader

@contextmanager
def open(filename, **credentials):
    """
    A contextmanager to open the KeePass file with `filename`. Use a `password`
    and/or `keyfile` named argument for decryption.
    
    Files are identified using their signature and a reader suitable for 
    the file format is intialized and returned.
    
    Note: `keyfile` is currently not supported for v3 KeePass files.
    """
    kdb = None
    try:
        with io.open(filename, 'rb') as stream:
            signature = read_signature(stream)
            cls = get_kdb_class(signature)
            kdb = cls(stream, **credentials)
            yield kdb
            kdb.close()
    except:
        if kdb: kdb.close()
        raise

def get_kdb_class(sig):
    if sig[0] == 0x9AA2D903:
        # KeePass 2.x
        # regarding the version:
        # KeePass 2.07 has version 1.01, 
        # 2.08 has 1.02,
        # 2.09 has 2.00, 2.10 has 2.02, 2.11 has 2.04,
        # 2.15 has 3.00.
        # The first 2 bytes are critical (i.e. loading will fail, if the
        # file version is too high), the last 2 bytes are informational.
        if sig[1] == 0xB54BFB67 and sig[2] <= 3:
            return KDB4Reader
        # KeePass 1.x (the version field was deeper in the header then)
        elif sig[1] == 0xB54BFB66:
            raise IOError('KeePass pre2.x not supported.')
        # KeePass pre2.x
        elif sig[1] == 0xB54BFB65:
            #raise IOError('KeePass 1.x/KeePassX not supported.')
            return KDB3Reader
        else:
            #TODO add dict or something to add support for other signatures
            IOError('Unknown file signature.')
    raise IOError('Unknown file signature.')

