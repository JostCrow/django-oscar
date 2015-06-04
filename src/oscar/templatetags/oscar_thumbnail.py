import re

from django.conf import settings
from django.utils.encoding import smart_str
from django.template import Library, TemplateSyntaxError

RE_SIZE = re.compile(r'(\d+)x(\d+)$')
kw_pat = re.compile(r'^(?P<key>[\w]+)=(?P<value>.+)$')

register = Library()


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


class ThumbnailNode(settings.OSCAR_THUMBNAIL_NODE):
    def __init__(self, parser, token):
        args = token.split_contents()
        tag = args[0]

        if len(args) > 4 and args[-2] == 'as':
            self.context_name = args[-1]
            args = args[:-2]
        else:
            self.context_name = None

        if len(args) < 3:
            raise TemplateSyntaxError(
                "Invalid syntax. Expected "
                "'{%% %s source size [option1 option2 ...] %%}' or "
                "'{%% %s source size [option1 option2 ...] as variable %%}'" %
                (tag, tag))

        self.opts = {}

        # The first argument is the source file.
        self.source_var = parser.compile_filter(args[1])

        # The second argument is the requested size. If it's the static "10x10"
        # format, wrap it in quotes so that it is compiled correctly.
        size = args[2]
        match = RE_SIZE.match(size)
        if match:
            size = '"%s"' % size
        self.opts['size'] = parser.compile_filter(size)

        # All further arguments are options.
        args_list = split_args(args[3:]).items()
        for arg, value in args_list:
            if value and value is not True:
                value = parser.compile_filter(value)
            self.opts[arg] = value

        self.file_ = parser.compile_filter(args[1])
        self.geometry = parser.compile_filter(args[2])
        self.options = []
        self.as_var = None
        self.nodelist_file = None

        if args[-2] == 'as':
            options_args = args[3:-2]
        else:
            options_args = args[3:]

        for bit in options_args:
            m = kw_pat.match(bit)
            if not m:
                raise TemplateSyntaxError(self.error_msg)
            key = smart_str(m.group('key'))
            expr = parser.compile_filter(m.group('value'))
            self.options.append((key, expr))

        if args[-2] == 'as':
            self.as_var = args[-1]
            self.nodelist_file = parser.parse(('empty', 'endthumbnail',))
            if parser.next_token().contents == 'empty':
                self.nodelist_empty = parser.parse(('endthumbnail',))
                parser.delete_first_token()


@register.tag(name="oscar_thumbnail")
def oscar_thumbnail(parser, token):
    """
    Creates a thumbnail via the package defined in the oscar settings.

    The default thumbnail will be the one from sorl thumbnail.
    """
    return ThumbnailNode(parser, token)
