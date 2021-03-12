from rest_framework import renderers
from rest_framework.utils import encoders, json
from rest_framework.exceptions import ErrorDetail
from rest_framework.compat import (
    INDENT_SEPARATORS, LONG_SEPARATORS, SHORT_SEPARATORS, coreapi, coreschema,
    pygments_css, yaml
)


class UserRenderer(renderers.JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into JSON, returning a bytestring.
        """
        if data is None:
            return b''

        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        if indent is None:
            separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS
        else:
            separators = INDENT_SEPARATORS

        #raise Exception(issubclass(type(data['detail']), ErrorDetail))
        raise Exception(data)
        if issubclass(type(data['detail']), ErrorDetail):
            ret = json.dumps({'validation_error': 'Ya realno creyzi'})
        else:
            ret = json.dumps(
                data, cls=self.encoder_class,
                indent=indent, ensure_ascii=self.ensure_ascii,
                allow_nan=not self.strict, separators=separators
            )

        # We always fully escape \u2028 and \u2029 to ensure we output JSON
        # that is a strict javascript subset.
        # See: http://timelessrepo.com/json-isnt-a-javascript-subset
        ret = ret.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
        return ret.encode()
