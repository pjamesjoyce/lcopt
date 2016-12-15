from data_structures import Substance, Product

"""Set up global substances"""

BR = Substance("Bauxite Residue")
Si = Substance("Quartz")
C = Substance("Graphite")

IP_C0S0 = Product("IP_C0S0", description="Precursor mix, 100% BR", defaults = [(BR, 100)])
IP_C160S0 = Product("IP_C160S0", description="Precursor mix, 98.4% BR, 1.6% C", defaults = [(BR, 98.4), (C, 1.6)])
IP_C144S10 = Product("IP_C144S10", description="Precursor mix, 88.56% BR, 1.44% C, 10% Si", defaults = [(BR, 88.56), (C, 1.44), (Si, 10)])

default_compositions = [IP_C0S0, IP_C160S0, IP_C144S10]

if __name__ == '__main__':
	for c in default_compositions:
		print ("{} : {}".format(c.name, c.list_composition()))


