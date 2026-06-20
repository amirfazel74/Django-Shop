from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product-list'),
    path('category/<str:cat>/', views.ProductListView.as_view(), name='product-list-by-category'),
    path('brand/<str:brand>/', views.ProductListView.as_view(), name='product-list-by-brand'),
    path('<slug:slug>', views.ProductDetailView.as_view(), name='product-detail'),
    path('favorite/', views.AddProductFavorite.as_view(), name='add-product-favorite'),
    path('cart/add/', views.AddToCartView.as_view(), name='add-to-cart'),
    path('categories-component/', views.product_categories_component, name='categories-component'),
    path('brands-component/', views.product_brands_component, name='brands-component'),
]
