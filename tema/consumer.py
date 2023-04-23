"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, kwargs=kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.name = kwargs["name"]

    def run(self):
        it0 = 0
        while (it0 < len(self.carts)):
            id = self.id = self.marketplace.new_cart()
            it1 = 0
            while (it1 < len(self.carts[it0])):
                it2 = 0
                while (it2 < self.carts[it0][it1]["quantity"]):
                    if (self.carts[it0][it1]["type"] == "add"):
                        result = self.marketplace.add_to_cart(id, self.carts[it0][it1]["product"])
                        if (result):
                            it2 += 1
                        else:
                            sleep(self.retry_wait_time)
                    if (self.carts[it0][it1]["type"] == "remove"):
                        self.marketplace.remove_from_cart(id, self.carts[it0][it1]["product"])
                        it2 += 1
                it1 += 1
            cart_cont = self.marketplace.place_order(id)
            for i in range(len(cart_cont)):
                print(self.name + " bought " + str(cart_cont[i]))
            it0 += 1
