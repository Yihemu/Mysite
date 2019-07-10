from django.shortcuts import render_to_response, get_object_or_404, render
from .models import BlogType, Blog
from django.db.models import Count
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from read_statistics.utils import read_statistics_once_read
from comment.models import Comment
import markdown


# Create your views here.


# 分页功能
def get_context_common(request, blogs):
    paginator = Paginator(blogs, 7)  # 每10页进行分页
    page_num = request.GET.get('page', 1)  # 获取url的页面参数 （GET请求）
    page_of_blogs = paginator.get_page(page_num)
    current_page_num = page_of_blogs.number  # 获取当前页码
    # 获取但前页面前后两个页面
    page_range = [x for x in range(int(current_page_num) - 2, int(current_page_num) + 3) if
                  0 < x <= paginator.num_pages]

    # 加上深略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)


    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_range'] = page_range
    context['page_of_blogs'] = page_of_blogs
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['blog_dates'] = Blog.objects.dates('create_time', 'month', order="DESC")
    return context


# 博客列表
def blog_list(request):
    blogs = Blog.objects.all()
    context = get_context_common(request, blogs)
    return render(request, 'blog_list.html', context)


# 博客的详细信息
def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request, blog)
    blog.content = markdown.markdown(blog.content, extensions=[
        'markdown.extensions.extra',  # 拓展
        'markdown.extensions.codehilite',  # 语法高亮拓展
        'markdown.extensions.toc',  # 允许自动生成目录
    ])
    blog_content_type = ContentType.objects.get_for_model(blog)
    comments = Comment.objects.filter(content_type=blog_content_type, object_id=blog.pk)

    context = {}
    context['blog'] = blog
    # 上下文
    context['previous_blog'] = Blog.objects.filter(create_time__gt=blog.create_time).last()
    context['next_blog'] = Blog.objects.filter(create_time__lt=blog.create_time).first()
    context['comments'] = comments
    response = render(request, 'blog_detail.html', context)
    response.set_cookie(read_cookie_key, 'true')
    return response


# 根据博客分类列出博文
def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blog_all_list = Blog.objects.filter(blog_type=blog_type)  # 过滤器
    context = get_context_common(request, blog_all_list)
    context['blog_type'] = blog_type
    return render(request, 'blogs_with_type.html', context)


# 根据博客日期分类
def blogs_with_date(request, year, month):
    blog_all_list = Blog.objects.filter(create_time__year=year, create_time__month=month)  # 过滤器
    context = get_context_common(request, blog_all_list)
    context['blogs_with_date'] = '%s年%s月' % (year, month)
    return render(request, 'blogs_with_date.html', context)

