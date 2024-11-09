# from django.urls import path
# from . import views

# urlpatterns = [
#     path('product/', views.product_page, name='product_page'),
#     path('order/<int:user_id>/', views.order_page, name='order_page'),
#     path('update_quantity/', views.update_quantity, name='update_quantity'),
#     path('create_order/', views.create_order, name='create_order'),
#     path('place_order/', views.place_order, name='place_order'),
#     path('orders/<int:user_id>/', views.view_orders, name='view_orders'),
    
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('product/', views.product_page, name='product_page'),
    path('order/<int:user_id>/', views.order_page, name='order_page'),
    path('create_order/', views.create_order, name='create_order'),
    path('update_quantity/', views.update_quantity, name='update_quantity'),
]
