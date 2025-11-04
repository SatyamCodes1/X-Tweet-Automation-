# Minimal fallback imghdr for Python 3.13+
# Only supports basic JPEG and PNG detection (good enough for Tweepy)
import binascii

def what(file, h=None):
    if h is None:
        if hasattr(file, 'read'):
            pos = file.tell()
            head = file.read(32)
            file.seek(pos)
        else:
            with open(file, 'rb') as f:
                head = f.read(32)
    else:
        head = h

    if head.startswith(b'\xff\xd8'):
        return 'jpeg'
    if head.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    return None
