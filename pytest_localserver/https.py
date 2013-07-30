# Copyright (C) 2010-2013 Sebastian Rahlf and others (see AUTHORS).
#
# This program is release under the MIT license. You can find the full text of
# the license in the LICENSE file.

import os.path
from pytest_localserver.http import ContentServer

#: default server certificate
DEFAULT_CERTIFICATE = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'server.pem')


class SecureContentServer (ContentServer):

    """
    Small test server which works just like :class:`http.Server` over HTTP::

        server = SecureContentServer(
            port=8080, key='/srv/my.key', cert='my.certificate')
        server.start()
        print 'Test server running at %s' % server.url
        server.serve_content(open('/path/to/some.file').read())
        # any call to https://localhost:8080 will get the contents of
        # /path/to/some.file as a response.

    To avoid *ssl handshake failures* you can import the `pytest-localserver
    CA`_ into your browser of choice.

    How to create a self-signed certificate
    ---------------------------------------

    If you want to create your own server certificate, you need `OpenSSL`_
    installed on your machine. A self-signed certificate consists of a
    certificate and a private key for your server. It can be created with the
    following command::

        openssl req -new -x509 -keyout server.pem -out server.pem -nodes

    Note that both key and certificate are in a single file now named
    ``server.pem``.

    How to create your own Certificate Authority
    --------------------------------------------

    Generate a server key and request for signing (csr). Make sure that the
    common name (CN) is your IP address/domain name (e.g. ``localhost``). ::

        openssl genrsa -des3 -out server.key 4096
        openssl req -new -key server.key -out server.csr

    Generate your own CA. Make sure that this time the CN is *not* your IP
    address/domain name (e.g. ``localhost CA``). ::

        openssl genrsa -des3 -out ca.key 4096
        openssl req -new -x509 -key ca.key -out ca.crt

    Sign the certificate signing request (csr) with the self-created CA that
    you made earlier. If you issue subsequent certificates and your browser
    already knows about previous ones simply increment the serial number. ::

        openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
            -set_serial 01 -out server.crt

    Make a server.key which doesn't cause HTTPSServer to prompt for a
    password::

        openssl rsa -in server.key -out server.key.insecure
        mv server.key server.key.secure
        mv server.key.insecure server.key

    Create a single file for both key and certificate::

        cat server.key server.crt > server.pem

    Now you only need to import ``ca.crt`` as a CA in your browser.

    Want to know more?
    ------------------

    This information was compiled from the following sources, which you might
    find helpful if you want to dig deeper into `pyOpenSSH`_, certificates and
    CAs:

    - http://code.activestate.com/recipes/442473/
    - http://www.tc.umn.edu/~brams006/selfsign.html
    -

    A more advanced tutorial can be found `here`_.

    .. _pytest-localserver CA: https://bitbucket.org/basti/pytest-localserver/src/tip/pytest_localserver/ca.crt
    .. _pyOpenSSH: https://launchpad.net/pyopenssl
    """

    def __init__(self, host='localhost', port=0,
                 key=DEFAULT_CERTIFICATE, cert=DEFAULT_CERTIFICATE):
        """
        :param key: location of file containing the server private key.
        :param cert: location of file containing server certificate.
        """
        super(SecureContentServer, self).__init__(host, port, (key, cert))


if __name__ == '__main__':

    import sys
    import time

    print('Using certificate %s.' % DEFAULT_CERTIFICATE)

    server = SecureContentServer()
    server.start()
    server.logging = True

    print('HTTPS server is running at %s' % server.url)
    print('Type <Ctrl-C> to stop')

    try:
        path = sys.argv[1]
    except IndexError:
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', 'README')

    server.serve_content(open(path).read(), 302)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\rstopping...')
    server.stop()
