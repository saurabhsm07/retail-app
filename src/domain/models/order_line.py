from dataclasses import dataclass

'''
UPDATES:
    -   Added @dataclass(unsafe_hash=True) = generate __hash__ method even if it contains mutable objects in it.
        By default it doesn't work.    
'''


@dataclass(unsafe_hash=True)
class OrderLine:
    order_id: str
    sku: str
    quantity: int
