from django.db.models import Count
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from site_module.models import SiteBanner
from utils.http_service import get_client_ip
from utils.convertors import group_list
from .models import Product, ProductCategory, ProductBrand, ProductVisit, ProductGallery, HazardClass
import json


# ====================================================================
# لیست محصولات (هماهنگ با فیلترهای چندگانه و سورتینگ)
# ====================================================================
class ProductListView(ListView):
    template_name = 'product_module/product_list.html'
    model = Product
    context_object_name = 'products'
    paginate_by = 12

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        # پیدا کردن گران‌ترین محصول برای تعیین سقف ماشین حساب قیمت
        max_price_product = Product.objects.order_by('-price').first()
        context['db_max_price'] = max_price_product.price if max_price_product else 20000000

        # ارسال دیتا برای سایدبار فیلترها
        context['brands'] = ProductBrand.objects.filter(is_active=True).annotate(products_count=Count('product'))
        context['hazard_classes'] = HazardClass.choices
        context['categories'] = ProductCategory.objects.filter(is_active=True, is_delete=False)

        # ارسال لیست انتخاب‌های کاربر به فرانت‌اند (برای اینکه چک‌باکس‌ها تیک‌خورده باقی بمانند)
        selected_categories = self.request.GET.getlist('category')
        cat_url = self.kwargs.get('cat')
        if cat_url and cat_url not in selected_categories:
            selected_categories.append(cat_url)
        context['selected_categories'] = selected_categories

        selected_brands = self.request.GET.getlist('brand')
        brand_url = self.kwargs.get('brand')
        if brand_url and brand_url not in selected_brands:
            selected_brands.append(brand_url)
        context['selected_brands'] = selected_brands

        context['selected_hazards'] = self.request.GET.getlist('hazard')

        # بنرها
        context['banners'] = SiteBanner.objects.filter(is_active=True,
                                                       position__iexact=SiteBanner.SiteBannerPositions.product_list)
        return context

    def get_queryset(self):
        # اضافه کردن prefetch_related برای سرعت بخشیدن به لود دیتابیس
        query = super().get_queryset().prefetch_related('category', 'brand')
        request: HttpRequest = self.request

        # 1. دریافت پارامترها به صورت لیست (getlist)
        selected_categories = request.GET.getlist('category')
        selected_brands = request.GET.getlist('brand')
        selected_hazards = request.GET.getlist('hazard')

        start_price = request.GET.get('start_price')
        end_price = request.GET.get('end_price')
        sort_by = request.GET.get('sort', 'newest')
        search_query = request.GET.get('q')

        # --- پشتیبانی از URL های قدیمی (مثل کلیک روی منوی سایت) ---
        cat_url = self.kwargs.get('cat')
        brand_url = self.kwargs.get('brand')
        if cat_url and cat_url not in selected_categories:
            selected_categories.append(cat_url)
        if brand_url and brand_url not in selected_brands:
            selected_brands.append(brand_url)

        # 2. اعمال فیلترها به صورت پویا
        if selected_categories:
            from django.db.models import Q
            q_objects = Q(category__url_title__in=selected_categories)
            # اگر پارامتری عدد بود، احتمالا آی‌دی دسته‌بندی است
            numeric_cats = [c for c in selected_categories if c.isdigit()]
            if numeric_cats:
                q_objects |= Q(category__id__in=numeric_cats)
            query = query.filter(q_objects).distinct()

        if selected_brands:
            query = query.filter(brand__url_title__in=selected_brands).distinct()

        if selected_hazards:
            query = query.filter(hazard_class__in=selected_hazards)

        if start_price and start_price.isdigit():
            query = query.filter(price__gte=int(start_price))

        if end_price and end_price.isdigit():
            query = query.filter(price__lte=int(end_price))
            
        if search_query:
            query = query.filter(title__icontains=search_query)

        # 3. اعمال مرتب‌سازی (Sort)
        if sort_by == 'cheap':
            query = query.order_by('price')
        elif sort_by == 'expensive':
            query = query.order_by('-price')
        elif sort_by == 'bestseller':
            # در صورتی که فیلد تعداد فروش در آینده اضافه کردید، اینجا قرار دهید
            # فعلا به عنوان پیش‌فرض بر اساس ID مرتب می‌کنیم
            query = query.order_by('-id')
        else:  # newest
            query = query.order_by('-id')

        return query


# ====================================================================
# جزئیات محصول
# ====================================================================
class ProductDetailView(DetailView):
    template_name = 'product_module/product_detail.html'
    model = Product
    context_object_name = 'product'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('category', 'complementary_safety_gears')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loaded_product = self.object
        request = self.request

        favorite_product_id = request.session.get("product_favorites")
        context['is_favorite'] = favorite_product_id == str(loaded_product.id)

        context['banners'] = SiteBanner.objects.filter(is_active=True,
                                                       position__iexact=SiteBanner.SiteBannerPositions.product_detail)
        context['galleries'] = ProductGallery.objects.filter(product_id=loaded_product.id).all()
        context['complementary_products'] = loaded_product.complementary_safety_gears.filter(is_active=True)

        user_ip = get_client_ip(self.request)
        user_id = self.request.user.id if self.request.user.is_authenticated else None

        has_been_visited = ProductVisit.objects.filter(ip__iexact=user_ip, product_id=loaded_product.id).exists()
        if not has_been_visited:
            new_visit = ProductVisit(ip=user_ip, user_id=user_id, product_id=loaded_product.id)
            new_visit.save()

        # Schema JSON-LD Generation
        schema_data = {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": loaded_product.title,
            "image": [
                request.build_absolute_uri(loaded_product.image.url) if loaded_product.image else ""
            ],
            "description": loaded_product.short_description or "",
            "sku": str(loaded_product.id),
            "offers": {
                "@type": "Offer",
                "url": request.build_absolute_uri(loaded_product.get_absolute_url()),
                "priceCurrency": "IRT",
                "price": loaded_product.price,
                "availability": "https://schema.org/InStock" if loaded_product.inventory > 0 else "https://schema.org/OutOfStock",
                "itemCondition": "https://schema.org/NewCondition"
            }
        }
        if loaded_product.brand:
            schema_data["brand"] = {
                "@type": "Brand",
                "name": loaded_product.brand.title
            }
            
        context['product_schema_json'] = json.dumps(schema_data)

        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": []
        }
        
        position = 1
        breadcrumb_schema["itemListElement"].append({
            "@type": "ListItem",
            "position": position,
            "name": "خانه",
            "item": request.build_absolute_uri('/')
        })
        position += 1
        
        first_category = loaded_product.category.first()
        if first_category:
            breadcrumb_schema["itemListElement"].append({
                "@type": "ListItem",
                "position": position,
                "name": first_category.title,
                "item": request.build_absolute_uri(f'/products/cat/{first_category.url_title}')
            })
            position += 1
            
        breadcrumb_schema["itemListElement"].append({
            "@type": "ListItem",
            "position": position,
            "name": loaded_product.title,
            "item": request.build_absolute_uri(loaded_product.get_absolute_url())
        })
        
        context['breadcrumb_schema_json'] = json.dumps(breadcrumb_schema)

        return context


# ====================================================================
# افزودن به علاقه‌مندی‌ها
# ====================================================================
class AddProductFavorite(View):
    def post(self, request):
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, pk=product_id, is_active=True, is_delete=False)
        request.session["product_favorites"] = product_id
        return redirect(product.get_absolute_url())


# ====================================================================
# افزودن به سبد خرید (Session-based)
# ====================================================================
class AddToCartView(View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        cart = request.session.get('cart', {})

        if product_id in cart:
            cart[product_id]['quantity'] += 1
        else:
            cart[product_id] = {'quantity': 1}

        request.session['cart'] = cart
        return redirect(request.META.get('HTTP_REFERER', '/'))


# ====================================================================
# کامپوننت‌های دسته‌بندی و برند
# ====================================================================
def product_categories_component(request: HttpRequest):
    product_categories = ProductCategory.objects.filter(is_active=True, is_delete=False)
    context = {
        'categories': product_categories
    }
    return render(request, 'product_module/components/product_categories_component.html', context)


def product_brands_component(request: HttpRequest):
    product_brands = ProductBrand.objects.annotate(products_count=Count('product')).filter(is_active=True)
    context = {
        'brands': product_brands
    }
    return render(request, 'product_module/components/product_brands_component.html', context)
