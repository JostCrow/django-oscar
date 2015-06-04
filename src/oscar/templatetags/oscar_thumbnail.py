from django.conf import settings
from django.template import Library

register = Library()


class ThumbnailNode(settings.OSCAR_THUMBNAIL_NODE):
    def __init__(self, source, sizes):
        self.source = source
        self.source_var = source
        self.context_name = None
        self.geomery = sizes
        self.options = []
        self.as_var = None
        self.nodelist_file = None

    pass


@register.simple_tag(name="oscar_thumbnail")
def oscar_thumbnail(source, sizes):
    """
    Creates a thumbnail via the package defined in the oscar settings.

    The default thumbnail will be the one from sorl thumbnail.
    """
    return ThumbnailNode(source, sizes)
