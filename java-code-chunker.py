import src.java-code-chunker as CHUNKER
import javalang
import re
import sys
import inspect
from pathlib import Path

def get_method_start_end(method_node):
    startpos  = None
    endpos    = None
    startline = None
    endline   = None
    for path, node in tree:
        if startpos is not None and method_node not in path:
            endpos = node.position
            endline = node.position.line if node.position is not None else None
            break
        if startpos is None and node == method_node:
            startpos = node.position
            startline = node.position.line if node.position is not None else None
    print(startpos)
    print(endpos)
    print(startline)
    print(endline)
    return startpos, endpos, startline, endline

def get_method_text(startpos, endpos, startline, endline, last_endline_index):
    if startpos is None:
        return "", None, None, None
    else:
        startline_index = startline - 1 
        endline_index = endline - 1 if endpos is not None else None 

        # 1. check for and fetch annotations
        if last_endline_index is not None:
            for line in codelines[(last_endline_index + 1):(startline_index)]:
                if "@" in line: 
                    startline_index = startline_index - 1
        meth_text = "<ST>".join(codelines[startline_index:endline_index])
        meth_text = meth_text[:meth_text.rfind("}") + 1] 

        # 2. remove trailing rbrace for last methods & any external content/comments
        # if endpos is None and 
        if not abs(meth_text.count("}") - meth_text.count("{")) == 0:
            # imbalanced braces
            brace_diff = abs(meth_text.count("}") - meth_text.count("{"))

            for _ in range(brace_diff):
                meth_text  = meth_text[:meth_text.rfind("}")]    
                meth_text  = meth_text[:meth_text.rfind("}") + 1]     

        meth_lines = meth_text.split("<ST>")  
        meth_text  = "".join(meth_lines)                   
        last_endline_index = startline_index + (len(meth_lines) - 1) 

        return meth_text, (startline_index + 1), (last_endline_index + 1), last_endline_index


def iterate(obj, tabs = "" ):
    print(tabs+str(type(obj)))
    tabs = tabs + "    "

    if isinstance(obj, (list, dict, map, set)): # (list, dict, map)):
        if len(obj) > 0:
            for item in obj:
                iterate(item, tabs)
    elif isinstance(obj, object):
        for var in vars(obj):
            print(tabs+str(var))
            value = getattr(obj, var)
            try:
                if value != None:                    
                    iterate(value, tabs)
            except TypeError as e:
                continue
                print(tabs+"TypeError, Value = "+str(value))
                print(tabs+str(e))
    else:
        print(obj)


if __name__ == "__main__":
    # Use the command parameter to gather data based on a file extension.
    training_data = list()
    if len(sys.argv) != 2 :
        print("Enter one and only one absolute or relative path to ")
        print("a directory containing the Java code to be chunked.")
    else:
        training_data = get_file_list(sys.argv[1], "*.java")
    # Declare a dict/lookup to abbreviate Java type declarations.
    declaration_types = { 
        javalang.tree.EnumDeclaration: "enum",
        javalang.tree.ClassDeclaration: "class", 
        javalang.tree.AnnotationDeclaration: "annotation",
        javalang.tree.InterfaceDeclaration: "interface"
    }
    # Loop through each file and pull key information as chunks
    failed_files = []
    chunks = []
    for training in training_data:
        tree, files_failing_parsing = CHUNKER.parseFile(training)
        failed_files = files_failing_parsing + failed_files

#        iterate(tree)
#        package_name = tree.package.name
        t = tree.types[0]
#        try:
#            for constant in t.body.constants:
#                print(t.name)
#                print(constant.name)
#        except AttributeError as e:
#            continue
        for declaration in t.body.declarations:
            if type(declaration) == javalang.tree.MethodDeclaration:
                print(declaration.name)
            elif type(declaration) == javalang.tree.FieldDeclaration:
                print(declaration.declarators[0].name)
        print(issubclass(type(t.body.constants[0]), javalang.tree.Node))
        print(t.body.constants[0].position)
        print(len(t.body.constants))
        print(issubclass(type(t.body.declarations[0]), javalang.tree.Node))
        print(t.body.declarations[0].position)
        print(len(t.body.declarations))

#         declaration_type = declaration_types.get(type(t))
#         lex = None
#         for field_node in tree.types[0].fields:
#             startp, endp, startl, endl = get_method_start_end(field_node)
#             field_text, startl, endl, lex = get_method_text(startp, endp, startl, endl, lex)
#             chunks.append( {
#                 "package": package_name,
#                 "type": declaration_type,
#                 "name": t.name,
#                 "field": field_text
#             } )

        # print(tree.imports)
        # print(type(t))
#         lex = None
#         for  method_node in t.methods:
#             startp, endp, startl, endl = get_method_start_end(method_node)
#             method_text, startl, endl, lex = get_method_text(startp, endp, startl, endl, lex)
#             chunks.append( {
#                 "package": package_name,
#                 "type": declaration_type,
#                 "name": t.name,
#                 "method": method_text
#             } )

    # Print statements for testing
    if len(files_failing_parsing) > 0:
        print("The files that were NOT parsed are:")
        for f in files_failing_parsing:
            print(f)
    print("Chunks\n------")
    for c in chunks:
        print(c)


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

