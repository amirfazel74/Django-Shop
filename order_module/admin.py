from django.contrib import admin
from . import models

class OrderDetailInline(admin.TabularInline):
    model = models.OrderDetail
    extra = 0
    verbose_name = 'آیتم سفارش'
    verbose_name_plural = 'اقلام سفارش'
    readonly_fields = ('product', 'count', 'final_price')
    
    # We want admins to view what was ordered, maybe not edit prices/counts randomly to avoid inconsistencies.
    # But if they need to, we can remove readonly_fields. For now, readonly is safer for paid orders.
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_paid:
            return ['product', 'count', 'final_price']
        return []

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_status_display', 'is_paid', 'shipping_method', 'payment_date')
    list_filter = ('is_paid', 'status', 'shipping_method')
    search_fields = ('id', 'user__username', 'mobile', 'payment_track_id', 'payment_ref_number', 'tracking_code')
    list_editable = ('is_paid',)
    readonly_fields = ('payment_date', 'payment_track_id', 'payment_ref_number')
    inlines = [OrderDetailInline]

    fieldsets = (
        ('اطلاعات پایه سفارش', {
            'fields': (
                ('user', 'is_paid'),
                'status'
            )
        }),
        ('اطلاعات مالی و پرداخت (زیبال)', {
            'classes': ('collapse',),
            'fields': (
                'payment_date',
                ('payment_track_id', 'payment_ref_number')
            )
        }),
        ('اطلاعات گیرنده و ارسال', {
            'fields': (
                ('first_name', 'last_name'),
                ('mobile', 'postal_code'),
                ('province', 'city'),
                'address'
            )
        }),
        ('وضعیت مرسوله', {
            'fields': (
                ('shipping_method', 'shipping_cost'),
                'tracking_code'
            )
        })
    )

    def get_status_display(self, obj):
        return obj.get_status_display()
    get_status_display.short_description = 'وضعیت سفارش'
