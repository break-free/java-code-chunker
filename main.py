import src.java_code_chunker as JCC 
import sys
import tiktoken

if __name__ == "__main__":
    # Use the command parameter to gather data based on a file extension.
    training_data = list()
    if len(sys.argv) != 2 :
        print("Enter one and only one absolute or relative path to ")
        print("a directory containing the Java code to be chunked.")
    else:
        training_data = JCC.get_file_list(sys.argv[1], "*.java")

    # Loop through each file and pull key information as chunks
    chunks = []
    failed_files = []
    
    for file in training_data:
        codelines = JCC.get_code_lines(file)
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

