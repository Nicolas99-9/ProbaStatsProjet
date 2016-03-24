import itertools
def function(n):
    somme = 0
    for x in itertools.product(range(5),repeat=2):
        print(x)


function(5)

