from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Item, Order, OrderItem
# from django.urls import reverse
from django.utils import timezone
from django.http import Http404, JsonResponse
from django.core.exceptions import ValidationError
import json
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date

def product_page(request):
    users = User.objects.all()
    items = Item.objects.all()
    context = {
        'users': users,
        'items': items,
    }
    return render(request, 'api/product_page.html', context)



@csrf_exempt
def order_page(request, user_id):
    print(f"Debug: Request received for user_id={user_id}")  # Check if the request is reaching the view
    
    selected_date = request.GET.get('selected_date')
    print(f"Debug: Selected date={selected_date}")  # Verify if the selected date is being received
    
    # if not selected_date:
    #     print("Debug: No selected date found")
    #     return render(request, 'order_page.html', {'error': 'No selected date provided'})
    try:
        if selected_date:
            # Filter by user_id and selected date
            orders = Order.objects.filter(user_id=user_id, date=selected_date)
        else:
            # If no date is selected, return all orders for the user
            orders = Order.objects.filter(user_id=user_id)
        
        print(f"Debug: Orders fetched - {orders}")  # Ensure orders are fetched correctly
    # try:
    #     orders = Order.objects.filter(user_id=user_id, date=selected_date)
    #     print(f"Debug: Orders fetched - {orders}")  # Ensure orders are fetched correctly
    except Exception as e:
        print(f"Debug: Error fetching orders - {e}")
        return render(request, 'api/order_page.html', {'error': str(e)})
    
    return render(request, 'api/order_page.html', {'orders': orders, 'user': request.user, 'selected_date': selected_date})






@csrf_exempt
def create_order(request):
    print(request.POST)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(data)
            user_id = data.get("user_id")
            order_date = data.get("order_date")
            items = data.get("items")

            if not user_id or not order_date or not items:
                return JsonResponse({"error": "Invalid data provided"}, status=400)

            user = get_object_or_404(User, id=user_id)
            # order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
            order_date = parse_date(order_date)
            # print(order_date)
            if not order_date:
                return JsonResponse({"error": "Invalid order date format"}, status=400)
            
            for item_data in items:
                item_id = item_data.get("item_id")
                if not item_id:
                    return JsonResponse({"error": "Item ID missing in request"}, status=400)
                
                if Order.objects.filter(user=user, order_date=order_date, order_items__item_id=item_id).exists():
                    return JsonResponse(
                        {"error": f"Order for item ID {item_id} already exists on {order_date}"}, status=400
                    )


            # print(f"Parsed order date: {order_date}")
            order = Order.objects.create(user=user, order_date=order_date)

            for item_data in items:
                item_id = item_data.get("item_id")
                quantity = item_data.get("quantity" ,1)
                total_price = item_data.get("total_price", "0.00")
                instruction = item_data.get("instruction", "")



                if not item_id or not quantity:
                    return JsonResponse({"error": "Item data is incomplete"}, status=400)


                item = get_object_or_404(Item, id=item_id)
                
                OrderItem.objects.create(
                    order=order,
                    item=item,
                    quantity=quantity,
                    total_price=total_price,
                    instruction=instruction
                )

            return JsonResponse({"message": "Order created successfully"})
        except Exception as e:
            print(str(e))
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def update_quantity(request):
    if request.method == "POST":
        try:
            # Parse incoming form data
            data = json.loads(request.body)
            item_id = data.get("item_id")
            action = data.get("action")
            user_id = data.get("user_id")
            order_date = data.get("order_date")

            # Validate essential data
            if not item_id or not action or not user_id or not order_date:
                return JsonResponse({"error": "Invalid data provided"}, status=400)

            order_date = parse_date(order_date)
            item = get_object_or_404(Item, id=item_id)
            order = get_object_or_404(Order, user_id=user_id, item=item, order_date=order_date)

            # Update quantity based on action
            if action == "increment":
                order.quantity += 1
            elif action == "decrement" and order.quantity > 1:
                order.quantity -= 1
            else:
                return JsonResponse({"error": "Invalid action or quantity too low"}, status=400)

            # Update total price and save
            order.total_price = order.quantity * item.unit_price
            order.save()

            return JsonResponse({
                "quantity": order.quantity,
                "total_price": str(order.total_price)
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


def order_page_view(request, user_id):
    selected_date = request.GET.get('selected_date')
    user = get_object_or_404(User, id=user_id)
    
    # Filter orders for the selected user and date
    orders = OrderItem.objects.filter(order__user=user, order__order_date=selected_date)

    return render(request, 'orders_page.html', {
        'order': user,
        'selected_date': selected_date,
        'orders': orders
    })