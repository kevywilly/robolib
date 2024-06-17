import atexit
import threading
import time
from abc import abstractmethod

import traitlets
from traitlets.config.configurable import Configurable

from robolib.log import logger, pretty


class Node(Configurable):
    frequency = traitlets.Float(default_value=10).tag(config=True)
    pretty = pretty
    logger = logger

    def __init__(self, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self._thread = None
        self._running = False
        atexit.register(self._shutdown)

    def _loading(self):
        pretty(f"Loading {self.__class__.__name__} Node")

    def _loaded(self):
        pretty(f"Loaded {self.__class__.__name__} Node")

    def _started(self):
        pretty(f"{self.__class__.__name__} Node is running at {self.frequency} HZ")

    @abstractmethod
    def spinner(self):
        pass

    def shutdown(self):
        pass

    def _spin(self):
        while self._running:
            self.spinner()
            time.sleep(1.0 / self.frequency)

    def spin(self, frequency: int = 10):
        self.frequency = frequency
        self._running = True
        self._thread = threading.Thread(target=self._spin)
        self._thread.daemon = True
        self._thread.start()
        self._started()

    def spin_once(self):
        self.spinner()

    def _shutdown(self):
        print(f'{self.__class__.__name__} shutting down')
        self.shutdown()
        self._running = False
        if self._thread:

            try:
                self._thread.join()
            except Exception as ex:
                logger.warning(f'{ex.__str__()}')
