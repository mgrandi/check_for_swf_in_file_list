REQUESTS_ITER_CONTENT_CHUNK_SIZE = 3

'''
see:
https://en.wikipedia.org/wiki/SWF
https://web.archive.org/web/20130202203813/http://wwwimages.adobe.com/www.adobe.com/content/dam/Adobe/en/devnet/swf/pdf/swf-file-format-spec.pdf

The SWF header
All SWF files begin with the following header. The types are defined in Chapter 1: Basic Data Types.

Field       Type                Comment
-----       -----               --------
Signature   UI8                 Signature byte:
                                "F" indicates uncompressed
                                "C" indicates a zlib compressed SWF (SWF 6 and later only)
                                "Z" indicates a LZMA compressed SWF (SWF 13 and later only)
Signature   UI8                 Signature byte always "W"
Signature   UI8                 Signature byte always "S"
'''

ACCEPTABLE_SWF_MAGIC_NUMBERS = [
    b"CWS",
    b"FWS"
    b"ZWS"
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"