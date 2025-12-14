from django.shortcuts import render
from .models import MenuItem

def home(request):
    return render(request, 'home.html')

def menu(request):
    items = MenuItem.objects.all().order_by('category', 'name')
    # Группируем по категориям
    menu_dict = {}
    for item in items:
        cat_display = dict(MenuItem.CATEGORY_CHOICES)[item.category]
        menu_dict.setdefault(cat_display, []).append(item)
    return render(request, 'menu.html', {'menu_items': menu_dict})
