from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

DEFAULT_PAGE_SIZE = 25

def paginate_queryset(queryset, request, page_size=DEFAULT_PAGE_SIZE):
    """
    Generic pagination utility for any queryset
    Returns:
        - paginated queryset
        - paginator object
    """
    paginator = Paginator(queryset, page_size)
    page_number = request.GET.get('page')
    
    try:
        paginated_queryset = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        paginated_queryset = paginator.page(paginator.num_pages)
    
    return paginated_queryset, paginator
