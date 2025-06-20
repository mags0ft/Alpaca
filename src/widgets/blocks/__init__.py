# __init__.py

import re

from .latex import LatexRenderer
from .text import Text, GeneratingText, EditingText
from .table import Table
from .code import Code
from .separator import Separator

from .. import attachments
from ...sql_manager import generate_uuid, Instance as SQL

patterns = [
    ('code', re.compile(r'```([a-zA-Z0-9_+\-]*)\n(.*?)\n\s*```', re.DOTALL)),
    ('code', re.compile(r'`(\w*)\n(.*?)\n\s*`', re.DOTALL)),
    ('latex', re.compile(r'\\\[\n*?(.*?)\n*?\\\]|\$+\n*?(.*?)\$+\n*?', re.DOTALL)),
    ('table', re.compile(r'((?:\| *[^|\r\n]+ *)+\|)(?:\r?\n)((?:\|[ :]?-+[ :]?)+\|)((?:(?:\r?\n)(?:\| *[^|\r\n]+ *)+\|)+)', re.MULTILINE)),
    ('line', re.compile(r'\n\n(\-{3,})\n\n', re.DOTALL)),
    ('line', re.compile(r'^(\-{3,})',  re.DOTALL))
]


def text_to_block_list(content:str) -> list:
    blocks = []
    pos = 0
    for pattern_name, pattern in patterns:
        for match in pattern.finditer(content[pos:]):
            match_start, match_end = match.span()
            if pos < (match_start) and content[pos:(match_start)].strip():
                if len(blocks) > 0 and isinstance(blocks[-1], Text):
                    blocks[-1].append_content(content[pos:(match_start)])
                else:
                    blocks.append(Text(content=content[pos:(match_start)]))
            if pattern_name == "code":
                if match.group(1).lower() == 'latex':
                    blocks.append(LatexRenderer(content=match.group(2)))
                else:
                    blocks.append(Code(content=match.group(2), language=match.group(1)))
            elif pattern_name == "table":
                blocks.append(Table(content=content[match_start:match_end]))
            elif pattern_name == "latex":
                expression = match.group(1)
                if not expression:
                    expression = match.group(2)
                if '\\' in expression:
                    blocks.append(LatexRenderer(content=expression))
                elif expression.strip():
                    if len(blocks) > 0 and isinstance(blocks[-1], Text):
                        blocks[-1].append_content(expression)
                    else:
                        blocks.append(Text(content=expression))
            elif pattern_name == "line":
                blocks.append(Separator(content=match.group(1)))
            pos = match_end

    if pos < len(content):
        normal_text = content[pos:]
        if normal_text.strip():
            if len(blocks) > 0 and isinstance(blocks[-1], Text):
                blocks[-1].append_content(content[pos:])
            else:
                blocks.append(Text(content=content[pos:]))

    return blocks

