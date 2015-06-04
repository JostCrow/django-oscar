import re
import logging

from django.conf import settings
from django.template import Library, TemplateSyntaxError

register = Library()

logger = logging.getLogger('oscar.thumbnail_template')


def split_args(args):
    """
    Split a list of argument strings into a dictionary where each key is an
    argument name.
    An argument looks like ``crop``, ``crop="some option"`` or ``crop=my_var``.
    Arguments which provide no value get a value of ``True``.
    """
    args_dict = {}
    for arg in args:
        split_arg = arg.split('=', 1)
        if len(split_arg) > 1:
            value = split_arg[1]
        else:
            value = True
        args_dict[split_arg[0]] = value
    return args_dict


class OscarThumbnailNode(settings.OSCAR_THUMBNAIL_NODE):
    as_var = context_name = None
    nodelist_file = None
    options = []
    opts = {}

    def __init__(self, parser, token):
        args = token.split_contents()
        tag = args[0]

        # Made it possible to use 'as' inside the template
        if len(args) > 4 and args[-2] == 'as':
            self.as_var = self.context_name = args[-1]
            args = args[:-2]

        if len(args) < 3:
            raise TemplateSyntaxError(
                "Invalid syntax. Expected "
                "'{%% %s source size [option1 option2 ...] %%}' or "
                "'{%% %s source size [option1 option2 ...] as variable %%}'" %
                (tag, tag))

        # The first argument is the source file.
        self.file_ = self.source_var = parser.compile_filter(args[1])

        # The second argument is the requested size. If it's the static "10x10"
        # format, wrap it in quotes so that it is compiled correctly.
        self.geometry = self.opts['size'] = parser.compile_filter(args[2])

        # All further arguments are options.
        args_list = split_args(args[3:]).items()
        for arg, value in args_list:
            if value and value is not True:
                value = parser.compile_filter(value)
            self.opts[arg] = value
            self.options.append((arg, value))


@register.tag(name="oscar_thumbnail")
def oscar_thumbnail(parser, token):
    """
    Creates a thumbnail via the package defined in the oscar settings.

    The default thumbnail will be the one from sorl thumbnail.
    """
    node = OscarThumbnailNode(parser, token)
    logger.debug(node)
    for a in dir(node):
        logger.debug(a)
    return node
