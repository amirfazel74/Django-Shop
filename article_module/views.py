from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django.views.generic.list import ListView
from article_module.models import Article, ArticleCategory, ArticleComment


class ArticlesListView(ListView):
    model = Article
    paginate_by = 4
    template_name = 'article_module/articles_page.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ArticlesListView, self).get_context_data(*args, **kwargs)
        return context

    def get_queryset(self):
        query = super(ArticlesListView, self).get_queryset()
        query = query.filter(is_active=True).select_related('author').prefetch_related('selected_categories')
        category_name = self.kwargs.get('category')
        if category_name is not None:
            query = query.filter(selected_categories__url_title__iexact=category_name)
        return query


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article_module/article_detail_page.html'

    def get_queryset(self):
        query = super(ArticleDetailView, self).get_queryset()
        query = query.filter(is_active=True).select_related('author').prefetch_related('selected_categories', 'related_articles', 'related_products')
        return query

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data()
        article: Article = kwargs.get('object')
        context['comments'] = ArticleComment.objects.filter(article_id=article.id, parent=None).order_by('-create_date').prefetch_related('articlecomment_set')
        context['comments_count'] = ArticleComment.objects.filter(article_id=article.id).count()
        return context


def article_categories_component(request: HttpRequest):
    article_main_categories = ArticleCategory.objects.prefetch_related('articlecategory_set').filter(is_active=True, parent_id=None)

    context = {
        'main_categories': article_main_categories
    }
    return render(request, 'article_module/components/article_categories_component.html', context)


@login_required
@require_POST
def add_article_comment(request: HttpRequest):
    article_id = request.POST.get('article_id')
    article_comment = (request.POST.get('article_comment') or '').strip()
    parent_id = request.POST.get('parent_id') or None

    if not article_id or not article_comment:
        return HttpResponseBadRequest('Invalid comment data')

    article = get_object_or_404(Article, id=article_id, is_active=True)
    parent = None
    if parent_id:
        parent = get_object_or_404(ArticleComment, id=parent_id, article_id=article.id)

    ArticleComment.objects.create(
        article=article,
        text=article_comment,
        user_id=request.user.id,
        parent=parent,
    )

    context = {
        'comments': ArticleComment.objects.filter(article_id=article.id, parent=None).order_by('-create_date').prefetch_related('articlecomment_set'),
        'comments_count': ArticleComment.objects.filter(article_id=article.id).count()
    }
    return render(request, 'article_module/includes/article_comments_partial.html', context)
