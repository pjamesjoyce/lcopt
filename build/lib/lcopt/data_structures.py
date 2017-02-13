import uuid

class Error(Exception):
    """Base class for exceptions in this module"""
    pass

class DataStructureError(Error):
    """Exception raised for errors in the data structure

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
        


class Substance(object):
    """data structure for substances"""
    def __init__(self, name):
        super(Substance, self).__init__()
        self.name = name
        self.id = uuid.uuid4()

    def __unicode__(self):
        return u"Substance : {}".format(self.name)

    def __repr__(self):
        return "Substance : {}".format(self.name)

class Product(object):
    """data structure for products"""
    def __init__(self, name, description = "", **kwargs):
        super(Product, self).__init__()
        self.name = name
        self.description = description
        self.substances = []

        if 'defaults' in kwargs:
            for d in kwargs['defaults']:
                self.add_substance(d[0],d[1])

    def add_substance(self, substance, amount):
        """add a substance to a product - requires substance and amount"""
        if isinstance(substance, Substance):
            self.substances.append({"substance":substance, "amount":amount})
        else:
            raise DataStructureError("Failed adding {} to {}".format(substance, self.name), "Must be a substance")

    def list_substances(self):
        s_list = []
        for s in self.substances:
            s_list.append(s["substance"].name)
        return s_list

    def list_composition(self):
        s_list = []
        total = 0
        for s in self.substances:
            s_list.append([s["substance"].name,s["amount"]])
            total+= s["amount"]

        for s in s_list:
            s.append(s[1]/total)

        return s_list


if __name__ == '__main__':

    """ Run tests if executed from the command line """

    my_product = Product("Composition 1")
    foo = Substance("Foo")
    bar = Substance("Bar")
    my_product.add_substance(foo, 100)
    my_product.add_substance(bar, 300)
    print(my_product.list_composition())
    my_product2 = Product("Composition 2", description="Here's the description", defaults = [(foo, 75), (bar,25)])
    print (my_product2.description)
    print(my_product2.list_composition())

        