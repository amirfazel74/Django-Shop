from django.db.models import Count
from django.shortcuts import render
from django.views.generic.base import TemplateView
from product_module.models import Product, ProductCategory
from site_module.models import SiteSetting, FooterLinkBox, Slider
from utils.convertors import group_list
from django.views.generic import TemplateView
from .models import Slider
from article_module.models import Article


class HomeView(TemplateView):
    template_name = 'home_module/index_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sliders'] = Slider.objects.filter(is_active=True).order_by('order', '-id')

        latest_products = Product.objects.filter(is_active=True, is_delete=False).order_by('-id')[:12]
        most_visit_products = Product.objects.filter(is_active=True, is_delete=False).annotate(
            visit_count=Count('productvisit')).order_by('-visit_count')[:12]

        context['latest_products'] = group_list(latest_products)
        context['most_visit_products'] = group_list(most_visit_products)

        # تغییر مهم: فیلتر بر اساس show_in_home=True
        categories = list(ProductCategory.objects.annotate(
            products_count=Count('product_categories')
        ).filter(
            is_active=True,
            is_delete=False,
            show_in_home=True,  # فقط دسته‌بندی‌های منتخب صفحه اصلی
            products_count__gt=0
        )[:8])  # حداکثر ۸ دسته‌بندی

        categories_products = []
        for category in categories:
            item = {
                'id': category.id,
                'title': category.title,
                'image': category.image,
                'color': category.color,
                'products': list(category.product_categories.all()[:4])
            }
            categories_products.append(item)

        context['categories_products'] = categories_products
        
        # مقالات جدید
        latest_articles = Article.objects.filter(is_active=True).order_by('-create_date')[:4]
        context['latest_articles'] = latest_articles
        
        return context


def site_header_component(request):
    setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
    
    cart_count = 0
    if request.user.is_authenticated:
        from order_module.models import Order
        current_order = Order.objects.filter(is_paid=False, user_id=request.user.id).first()
        if current_order:
            cart_count = current_order.orderdetail_set.count()

    context = {
        'site_setting': setting,
        'cart_count': cart_count,
        'request': request
    }
    return render(request, 'shared/site_header_component.html', context)


def site_footer_component(request):
    setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
    footer_link_boxes = FooterLinkBox.objects.all()
    context = {
        'site_setting': setting,
        'footer_link_boxes': footer_link_boxes
    }
    return render(request, 'shared/site_footer_component.html', context)


class AboutView(TemplateView):
    template_name = 'home_module/about_page.html'

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        site_setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
        context['site_setting'] = site_setting
        return context
