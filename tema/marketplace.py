"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Lock
import logging
import logging.handlers
from time import gmtime
import unittest

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
        self.logger = logging.getLogger("marketplace")
        self.logger.setLevel(logging.INFO)
        file_hd = logging.handlers.RotatingFileHandler(filename="marketplace.log", maxBytes=512000, backupCount=5)
        file_hd.setLevel(logging.INFO)
        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_format.converter = gmtime
        file_hd.setFormatter(log_format)
        self.logger.addHandler(file_hd)

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        self.prod_lock.acquire()
        self.producers.append([])
        prod_id = len(self.producers) - 1
        self.logger.info("registered new producer with id %d", prod_id)
        self.prod_lock.release()
        return prod_id

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
        self.logger.info("publishing product %s from producer %d" % (str(product), producer_id))
        if len(self.producers[producer_id]) > self.queue_size_per_producer:
            self.logger.info("could not publish product: queue full")
            self.lock.release()
            return False
        self.producers[producer_id].append(product)
        self.logger.info("product sucessfully produced")
        self.lock.release()
        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.cart_lock.acquire()
        self.carts.append([])
        cart_id = len(self.carts) - 1
        self.logger.info("registered new cart with id %d", cart_id)
        self.cart_lock.release()
        return cart_id

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
        self.logger.info("adding product %s to cart %d" % (str(product), cart_id))
        for i in range(len(self.producers)):
            try:
                pos = self.producers[i].index(product)
                self.carts[cart_id].append((product, i))
                self.producers[i].pop(pos)
                self.logger.info("product successfully added to cart")
                self.lock.release()
                return True
            except ValueError:
                pass
        self.logger.info("could not add product: not available")
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
        self.logger.info("removing product %s from cart %d" % (str(product), cart_id))
        for i in range(len(self.carts[cart_id])):
            if self.carts[cart_id][i][0] == product:
                self.producers[self.carts[cart_id][i][1]].append(product)
                self.carts[cart_id].pop(i)
                self.logger.info("product successfully removed from cart")
                self.lock.release()
                return
        self.logger.info("could not remove product: no such product exists")
        self.lock.release()

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        return_order = [elem[0] for elem in self.carts[cart_id]]
        self.logger.info("created order for cart %d", cart_id)
        return return_order

class TestMarketplace(unittest.TestCase):
    def setUp(self):
        self.marketplace = Marketplace(1)

    def test_unique_producers(self):
        prod1 = self.marketplace.register_producer()
        prod2 = self.marketplace.register_producer()
        self.assertNotEqual(prod1, prod2)

    def test_publish(self):
        prod = self.marketplace.register_producer()
        result = self.marketplace.publish(prod, "item")
        self.assertTrue(result)

    def test_publish_full(self):
        prod = self.marketplace.register_producer()
        result = self.marketplace.publish(prod, "item")
        result = self.marketplace.publish(prod, "item2")
        result = self.marketplace.publish(prod, "item3")
        self.assertFalse(result)

    def test_unique_carts(self):
        cart1 = self.marketplace.new_cart()
        cart2 = self.marketplace.new_cart()
        self.assertNotEqual(cart1, cart2)

    def test_add_existing(self):
        prod = self.marketplace.register_producer()
        cart = self.marketplace.new_cart()
        result = self.marketplace.publish(prod, "item")
        result = self.marketplace.add_to_cart(cart, "item")
        self.assertTrue(result)

    def test_add_nonexisting(self):
        prod = self.marketplace.register_producer()
        cart = self.marketplace.new_cart()
        result = self.marketplace.add_to_cart(cart, "item")
        self.assertFalse(result)

    def test_place_order(self):
        prod = self.marketplace.register_producer()
        cart = self.marketplace.new_cart()
        result = self.marketplace.publish(prod, "item")
        result = self.marketplace.add_to_cart(cart, "item")
        result = self.marketplace.place_order(cart)
        self.assertIsNotNone(result)

    def test_remove_from_cart(self):
        prod = self.marketplace.register_producer()
        cart = self.marketplace.new_cart()
        result = self.marketplace.publish(prod, "item")
        result = self.marketplace.add_to_cart(cart, "item")
        self.marketplace.remove_from_cart(cart, "item")
        result = self.marketplace.place_order(cart)
        self.assertNotIn("item", result)