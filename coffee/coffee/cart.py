# cafe/cart.py
from main.models import MenuItem
class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, item_id, quantity=1):
        item_id = str(item_id)
        if item_id not in self.cart:
            self.cart[item_id] = {'quantity': 0}
        self.cart[item_id]['quantity'] += quantity
        self.save()

    def remove(self, item_id):
        item_id = str(item_id)
        if item_id in self.cart:
            del self.cart[item_id]
            self.save()

    def decrement(self, item_id):
        item_id = str(item_id)
        if item_id in self.cart:
            self.cart[item_id]['quantity'] = max(1, self.cart[item_id]['quantity'] - 1)
            self.save()

    def increment(self, item_id):
        item_id = str(item_id)
        if item_id in self.cart:
            self.cart[item_id]['quantity'] += 1
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        item_ids = self.cart.keys()
        items = MenuItem.objects.filter(id__in=item_ids, in_stock=True)
        cart = self.cart.copy()
        
        for item in items:
            item_id_str = str(item.id)
            if item_id_str in cart:
                quantity = cart[item_id_str]['quantity']
                cart[item_id_str]['item'] = item
                cart[item_id_str]['total_price'] = item.price * quantity  # ← добавили
        
        for data in cart.values():
            if 'item' in data and data.get('quantity', 0) > 0:
                yield data

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            item['quantity'] * item['item'].price
            for item in self
        )

    def clear(self):
        del self.session['cart']
        self.save()