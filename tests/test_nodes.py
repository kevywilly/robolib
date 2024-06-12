import time
import unittest

from robolib.nodes.node import Node

class HelloNode(Node):
    pass

class TestHandler(unittest.TestCase):

    def test_basic_node(self):
        hello = HelloNode()
        hello.spin(20)
        assert hello.frequency == 20


