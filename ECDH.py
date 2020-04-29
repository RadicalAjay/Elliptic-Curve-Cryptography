from collections import namedtuple
import random

point = namedtuple('point', ['x', 'y'])


class EC():
    '''Elliptic Curve'''

    def __init__(self, a, b, n):

        assert 0 < a < n and 0 < b < n and n > 2, 'parameters does not meet requirement'
        assert (4 * (a**3) + 27 * (b**2)) % n != 0, 'wrong curve'
        self.a = a
        self.b = b
        self.n = n
        self.inf = (0, 0)

    def on_curve(self, p):
        '''verifys if the point lie on the curve'''

        if p == self.inf:
            return True

        status = (p.y**2) % self.n == (p.x**3 + self.a * p.x + self.b) % self.n
        return status

    def generator(self):
        ''' returns a random generator from a list of generators for the curve'''
        perfect_squares = {}
        base = 1
        while True:
            perfect_square = pow(base, 2, self.n)
            if perfect_square in perfect_squares:
                break
            perfect_squares[perfect_square] = base
            base += 1

        generators = []
        for x in range(base):
            y_square = ((x**3) + self.a * x + self.b) % self.n
            if y_square in perfect_squares:
                pt1 = point(x, perfect_squares[y_square])
                pt2 = point(x, -perfect_squares[y_square] % self.n)
                generators.append(pt1)
                generators.append(pt2)
        # print(generators)

        # verify all the generators lie on the curve
        assert all(list(map(self.on_curve, generators)))
        return random.choice(generators)

    def xgcd(self, a, b):
        '''return (g, x, y) such that a*x + b*y = g = gcd(a, b)'''
        s0, s1, t0, t1 = 1, 0, 0, 1
        while b > 0:
            q, r = divmod(a, b)
            a, b = b, r
            s0, s1, t0, t1 = s1, s0 - q * s1, t1, t0 - q * t1
        return a, s0, t0

    def inv(self, a):
        '''return x such that (x * a) % self.n == 1'''
        g, x, y = self.xgcd(a, self.n)
        return x % self.n

    def point_addition(self, p, q):
        '''point addition of 2 points'''
        if p == self.inf:
            return q

        elif q == self.inf:
            return p

        elif p.x == q.x and p.y != q.y:
            return self.inf

        if p.x == q.x:
            s = ((3 * (p.x**2) + self.a) * self.inv(2 * p.y)) % self.n
        else:
            s = ((q.y - p.y) * self.inv(q.x - p.x)) % self.n

        x_coordinate = ((s * s) - p.x - q.x) % self.n
        y_coordinate = (s * (p.x - x_coordinate) - p.y) % self.n

        result = point(x_coordinate, y_coordinate)
        assert self.on_curve(result), f'failed with {p}, {q} = {result} and s:{s}'

        return result

    def multiply(self, p, n):
        '''Multiplies the point p for n times'''
        result = self.inf
        pt = p
        while n > 0:
            if n & 1 == 1:
                result = self.point_addition(result, pt)
            n, pt = n >> 1, self.point_addition(pt, pt)

        assert self.on_curve(result)
        return result

    def calc_public(self, gen, private):
        '''Calculate public_point from private number'''
        print('now', gen)
        return self.multiply(gen, private)


class DiffieHellman():
    '''Elliptic Curve Diffie Hellman(ECDH) Key Exchange'''

    def __init__(self, curve, gen, private):
        self.curve = curve
        self.gen = gen
        self.private = private

    def calc_public(self):
        '''Calculates public by multiplying generator with private integer'''
        return self.curve.multiply(self.gen, self.private)

    def calc_shared_key(self, public):
        '''calculates common shared key by multiplying our private with recieved public point'''
        return self.curve.multiply(public, self.private)


# last paramerter(n) must be a prime
curve = EC(1, 15, 19)


# ELLIPTIC CURVE DIFFIE HELLMAN:
gen = curve.generator()     # generator method returns a random point from list of generators
print('generator:', gen)

# PARTY 1
priv1 = 123         # a secret integer for party1
party1 = DiffieHellman(curve, gen, priv1)
pub1 = party1.calc_public()
print('Party1 public point:', pub1)


# PARTY 2
priv2 = 657         # a secret integer for party2
party2 = DiffieHellman(curve, gen, priv2)
pub2 = party2.calc_public()
print('Party2 public point:', pub2)


key_at_party1 = party1.calc_shared_key(pub2)
key_at_party2 = party2.calc_shared_key(pub1)

print()
assert key_at_party1 == key_at_party2
print('Party1 and Party2 shared a common key', key_at_party1)
