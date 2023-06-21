import src.code_chunker.parser as file_parser
import src.code_chunker.java_code as JCC
import sys
import tiktoken

if __name__ == "__main__":
    # Use the command parameter to gather data based on a file extension.
    training_data = list()
    if len(sys.argv) != 3:
        print("2 command parameters required: (1) Enter one and only one absolute or relative path")
        print("to a directory containing the code to be chunked. (2) Enter the file extension for ")
        print("the files that need to be chunked. (e.g. python3 main.py training/test java)")
        exit()
    else:
        fileExtension = "*." + sys.argv[2]
        training_data = file_parser.get_file_list(sys.argv[1], fileExtension)

    # Loop through each file and pull key information as chunks
    chunks = []
    failed_files = []
    
    if fileExtension == "*.java":
        for file in training_data:
            codelines = file_parser.get_code_lines(file)
            try:
                tree = JCC.parse_code(file, codelines)
            except JCC.ParseError as e:
                failed_files.append(str(file) + ": " + str(e))
            if tree != None:
                # The `try` statements could be amalgamated but using them 
                # separately for now to get as many chunks as possible.
                try:
                    chunks = chunks + JCC.chunk_constants(tree)
                except JCC.ChunkingError as e:
                    failed_files.append(str(file) + ": " + str(e))
                try:
                    chunks = chunks + JCC.chunk_constructors(tree, codelines)
                except JCC.ChunkingError as e:
                    failed_files.append(str(file) + ": " + str(e))
                try:
                    chunks = chunks + JCC.chunk_fields(tree, codelines)
                except JCC.ChunkingError as e:
                    failed_files.append(str(file) + ": " + str(e))
                try:
                    chunks = chunks + JCC.chunk_methods(tree, codelines)
                except JCC.ChunkingError as e:
                    failed_files.append(str(file) + ": " + str(e))
            else:
                failed_files.append(str(file) + ", has no tree!")
    
    else:
        inputExtension = sys.argv[2]
        print(f'''File extension type "{inputExtension}" is currently not supported.''')
        exit()

    attempts = len(training_data)
    failures = len(failed_files)
    print("Number of files attempted to be parsed = " + str(attempts) + ".")
    print("Number of failed files = " + str(failures) +
          ". Failure rate = " + "{:.2f}".format(failures/attempts*100) + "%")
    if failures:
        print("\nFiles that were not processed ("+str(failures)+"):")
        for file in failed_files:
            print("\t- "+file)

    encoding = tiktoken.get_encoding("cl100k_base")
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    total_tokens = 0
    num_chunks = len(chunks)
    for chunk in chunks:
        total_tokens = total_tokens + len(encoding.encode(str(chunk)))
    print("Number of chunks generated = " + str(num_chunks))
    print("Average number of tokens per chunk = " + 
          "{:.2f}".format(total_tokens/num_chunks))
    print("Chunks sample")
    print("-------------")
    for chunk in chunks[:10]:
        print(str(chunk))
    print("...")

