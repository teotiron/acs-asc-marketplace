"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, kwargs=kwargs)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.id = self.marketplace.register_producer()

    def run(self):
        while True:
            it1 = 0
            while (it1 < len(self.products)):
                it2 = 0
                while (it2 < self.products[it1][1]):
                    result = self.marketplace.publish(self.id, self.products[it1][0])
                    if (result):
                        it2 += 1
                        sleep(self.products[it1][2])
                    else:
                        sleep(self.republish_wait_time)
                it1 += 1
