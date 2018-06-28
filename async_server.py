# https://gist.github.com/justinfx/72581492b92444b1fb1116c0fc919cb5

import asyncore
import socket
from threading import Thread

# TODO: asyncore is deprecated in 3.6. Switch to ascynio
class AsyncServer(asyncore.dispatcher):
    def __init__(self, host, port, select_timeout=1):
        asyncore.dispatcher.__init__(self)
        self._server_thread = None
        self._sock_read_handler = None
        self.setTimeout(select_timeout)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def start(self):
        print("Looping")
        print("\n")
        # if self._server_thread is not None:
        #     return
        #
        # self._server_thread = Thread(target=asyncore.loop, kwargs={'timeout': self._timeout})
        # self._server_thread.daemon = True
        # self._server_thread.start()
        asyncore.loop(timeout=self._timeout)

    def stop(self):
        self.close()
        if self._server_thread is not None:
            thread, self._server_thread = self._server_thread, None
            thread.join()

    def setTimeout(self, timeout):
        if isinstance(timeout, int):
            self._timeout = timeout
        else:
            self._timeout = 1

    def setReadHandler(self, handler_func):
        if not callable(handler_func):
            print("Error: expected a function argument.")
            return

        class Handler(asyncore.dispatcher_with_send):
            def handle_close(self):
                print("Socket closed")
                self.close()

            def handle_read(self):
                print("Handling read")
                handler_func(self)

        print("Setting read handler")
        self._sock_read_handler = Handler

    def handle_accept(self):
        tup = self.accept()
        if tup is None: return

        sock, addr = tup
        if self._sock_read_handler is None:
            print("No handler. Refuse connection from %s." % repr(addr))
            sock.close()
            return

        print("Incoming connection from %s" % repr(addr))
        self._sock_read_handler(sock)
