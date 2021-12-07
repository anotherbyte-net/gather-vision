from django import template
from django.urls import reverse, resolve
from django.utils.html import format_html

register = template.Library()


@register.inclusion_tag("gather_vision/nav_link.html", takes_context=True)
def bs_nav_link(context, url_name, display: str = None, **kwargs):
    """Render a bootstrap nav anchor element."""
    item_url = reverse(url_name, kwargs=kwargs)
    if not display:
        view_class = resolve(item_url).func.view_class
        display = view_class.page_title
    is_active = context.request.path.startswith(item_url)
    return {
        "is_active": " active" if is_active else "",
        "url": item_url,
        "aria": format_html(' aria-current="page"') if is_active else "",
        "display": display,
    }


@register.simple_tag(takes_context=True)
def view_attr(context, attr):
    """Render an attribute from the view class."""
    view_class = resolve(context.request.path).func.view_class
    return getattr(view_class, attr)


@register.inclusion_tag("gather_vision/nav_breadcrumb.html", takes_context=True)
def bs_breadcrumb(context, *args):
    """Render a list of breadcrumbs."""
    items = []
    for url_name in args:
        item_url = reverse(url_name)
        view_class = resolve(item_url).func.view_class
        page_title = view_class.page_title
        items.append({"text": page_title, "url": item_url})
    return {"items": items}
