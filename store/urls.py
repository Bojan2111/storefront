from cgitb import lookup
from django.urls import path
from django.urls import include
# from rest_framework.routers import SimpleRouter # or DefaultRouter with jsonify capabilities...
from rest_framework_nested import routers
from . import views

# router = SimpleRouter()
router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('orders', views.OrderViewSet, basename='orders')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')
products_router.register('images', views.ProductImageViewSet, basename='product-images')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + products_router.urls + carts_router.urls

# urlpatterns = [
##  path('', include(router.urls)) # when having specific paths for different purposes - include router urls
#   path('products/', views.ProductList.as_view()),
#   path('products/<int:pk>/', views.ProductDetail.as_view()),
#   path('collections/', views.CollectionList.as_view()),
#   path('collections/<int:pk>/', views.CollectionDetail.as_view(), name='collection-detail'),
# ]