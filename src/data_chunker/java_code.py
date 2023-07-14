import javalang

# Declare a dict/lookup to abbreviate Java type declarations.
declaration_types = { 
    javalang.tree.AnnotationDeclaration: "annotation",
    javalang.tree.ClassDeclaration: "class", 
    javalang.tree.EnumDeclaration: "enumeration",
    javalang.tree.InterfaceDeclaration: "interface"
}

def get_node_start_end(tree: javalang.tree.CompilationUnit,
                       d_node: javalang.tree.Declaration) -> int | int | int | int:
    startpos  = None
    endpos    = None
    startline = None
    endline   = None
    for path, node in tree:
        if startpos is not None and d_node not in path:
            endpos = node.position
            endline = node.position.line if node.position is not None else None
            break
        if startpos is None and node == d_node:
            startpos = node.position
            startline = node.position.line if node.position is not None else None
    return startpos, endpos, startline, endline

def get_node_text(codelines: list, startpos, endpos, startline, endline, 
                  last_endline_index) -> str | int | int | int:

    if startpos is None:
        return "", None, None, None

    startline_index = startline - 1 
    endline_index = endline - 1 if endpos is not None else None 

    # 1. check for and fetch annotations
    if last_endline_index is not None:
        for line in codelines[(last_endline_index + 1):(startline_index)]:
            if "@" in line: 
                startline_index = startline_index - 1
    node_text = "<ST>".join(codelines[startline_index:endline_index])
    if "}" in node_text:
        node_text = node_text[:node_text.rfind("}") + 1] 

    # 2. remove trailing rbrace for last methods & any external content/comments
    # if endpos is None and 
    if not abs(node_text.count("}") - node_text.count("{")) == 0:
        # imbalanced braces
        brace_diff = abs(node_text.count("}") - node_text.count("{"))

        for _ in range(brace_diff):
            node_text  = node_text[:node_text.rfind("}")]    
            node_text  = node_text[:node_text.rfind("}") + 1]     

    node_lines = node_text.split("<ST>")  
    node_text  = "".join(node_lines)                   
    last_endline_index = startline_index + (len(node_lines) - 1) 
    
    return node_text, (startline_index + 1), (last_endline_index + 1), last_endline_index

def chunk_constants( tree: javalang.tree.CompilationUnit ) -> list :

    # Initialize return variables
    chunks = []
    # Initialize local variables
    t = None

    # Check that there is only one type in tree.types otherwise return
    if len(tree.types) == 1:
        t = tree.types[0]
    else:
        return chunks
    # Attempt to read the package name (throws an error sometimes)
    try:
        p_name = tree.package.name
    except AttributeError as e:
        raise ChunkingError("Package name does not exist, raised in " + 
                         chunk_constants.__name__)
    # Checks that the tree has constants (TODO: still neede?)
    if not hasattr(t.body, "constants"):
        return chunks
    # Loop through nodes of a given type.
    for constant in t.body.constants:
        c_string = constant.name
        arg_list = []
        if constant.arguments != None:
            for arg in constant.arguments:
                try:
                    arg_list.append(arg.value)
                except AttributeError as e:
                    raise ChunkingError("When adding constants from" + t.name + 
                                        ", raised in " + 
                                        chunk_constants.__name__ + 
                                        ": " + str(e))
            arg_string = ", ".join(arg_list)
            code = constant.name + "(" + arg_string + ")"
            chunks.append({"package": str(p_name),
                           "type": declaration_types.get(type(t)),
                           "typename": t.name,
                           "member": "constant",
                           "membername": constant.name,
                           "code": code})

    return chunks

def chunk_constructors(tree: javalang.tree.CompilationUnit,
                       codelines: list) -> list:
    node_type = javalang.tree.ConstructorDeclaration
    return chunk_node_type(tree, node_type, "constructor", codelines)

def chunk_fields(tree: javalang.tree.CompilationUnit,
                 codelines: list) -> list:
    node_type = javalang.tree.FieldDeclaration
    return chunk_node_type(tree, node_type, "field", codelines)

def chunk_methods(tree: javalang.tree.CompilationUnit,
                  codelines: list) -> list:
    node_type = javalang.tree.MethodDeclaration
    return chunk_node_type(tree, node_type, "method", codelines)



def chunk_node_type(tree: javalang.tree.CompilationUnit,
                    node_type: javalang.tree.Declaration,
                    mem_str: str,
                    codelines: list) -> list:
    # Initialize return variables
    chunks = []
    # Initialize local variables
    t = None
    # Check that there is only one type in tree.types otherwise return
    if len(tree.types) == 1:
        t = tree.types[0]
    else:
        return chunks
    # Attempt to read the package name (throws an error sometimes)
    try:
        p_name = tree.package.name
    except AttributeError as e:
        raise ChunkingError("Package name does not exist, raised in " + 
                         chunk_constants.__name__)
    # Loop through nodes of a given type.
    lex = None
    for _, node in tree.filter(node_type):
        startp, endp, startl, endl = get_node_start_end(tree, node)
        code, startl, endl, lex = get_node_text(
            codelines, startp, endp, startl, endl, lex
        )
        # Need this ternary operator since Fields have their names elsewhere
        mem_name = node.name if mem_str != "field" else node.declarators[0].name
        chunks.append({"package": p_name,
                       "type": str(declaration_types.get(type(t))),
                       "typename": t.name,
                       "member": mem_str,
                       "membername": mem_name,
                       "code": code})

    return chunks

def parse_code(code_path: str, 
               codelines: list) -> javalang.tree.CompilationUnit:

    # Initialize return values
    tree = None

    # Merge list of code lines into one string
    code_text = ''.join(codelines)

    # Attempt to parse file; failures are recorded for return.
    #tree = javalang.parse.parse( code_text )
    try:
        tree = javalang.parse.parse( code_text )
    except javalang.parser.JavaSyntaxError as e:
        raise ParseError("Syntax error raised as JavaSyntaxError")
    except javalang.tokenizer.LexerError as le:
        raise ParseError("Tokenizer error raised as LexerError")

    # For simplicity, consider files with anything other than one type as 
    # failed
    try:
        if tree != None and len( tree.types ) != 1:
            raise ParseError("More than one type in file, which is not " +
                             "allowed, raised in " + str(parse_code.__name__))
    except AttributeError as e:
        raise ParseError("Tree's types do not exist, raised in " + 
                         str(parse_code.__name__) + ", " + str(e))
    return tree

# Declare a couple of classes to catch exceptions, handled by calling
# code
class ChunkingError(Exception):
    pass

class ParseError(Exception):
    pass
