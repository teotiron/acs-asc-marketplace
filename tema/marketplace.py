"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Lock

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer
        self.producers = []
        self.carts = []
        self.lock = Lock()
        self.prod_lock = Lock()
        self.cart_lock = Lock()

    def get_lock(self):
        """
        Returns the lock to be used by all
        """
        return self.lock

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        self.prod_lock.acquire()
        self.producers.append([])
        id = len(self.producers) - 1
        self.prod_lock.release()
        return id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        self.lock.acquire()
        if (len(self.producers[producer_id]) > self.queue_size_per_producer):
            self.lock.release()
            return False
        self.producers[producer_id].append(product)
        self.lock.release()
        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.cart_lock.acquire()
        self.carts.append([])
        id = len(self.carts) - 1
        self.cart_lock.release()
        return id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        self.lock.acquire()
        for i in range(len(self.producers)):
            try:
                pos = self.producers[i].index(product)
                self.carts[cart_id].append((product, i))
                self.producers[i].pop(pos)
                self.lock.release()
                return True
            except ValueError:
                dummy = 1
        self.lock.release()
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        self.lock.acquire()
        for i in range(len(self.carts[cart_id])):
            if (self.carts[cart_id][i][0] == product):
                self.producers[self.carts[cart_id][i][1]].append(product)
                self.carts[cart_id].pop(i)
                self.lock.release()
                return
        self.lock.release()

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        return_order = [elem[0] for elem in self.carts[cart_id]]
        return return_order
