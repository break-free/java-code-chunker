import src.java-code-chunker as CHUNKER
import javalang
import re
import sys
import inspect
from pathlib import Path

if __name__ == "__main__":
  

#         lex = None
#         try:
#             tree = javalang.parse.parse(code_text)
#         except javalang.parser.JavaSyntaxError as e:
#             continue
#         for _, method_node in tree.filter(javalang.tree.MethodDeclaration):
#             startpos, endpos, startline, endline = get_method_start_end(method_node)
#             method_text, startline, endline, lex = get_method_text(startpos, endpos, startline, endline, lex)
#             if "@Test" not in method_text:
#                 methods.append(method_text)

#    print(methods[:3])

