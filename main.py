import src.java_code_chunker as JCC 
import sys

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
            try:
                chunks = chunks + JCC.chunk_constants(tree)
                chunks = chunks + JCC.chunk_constructors(tree, codelines)
                chunks = chunks + JCC.chunk_fields(tree, codelines)
                chunks = chunks + JCC.chunk_methods(tree, codelines)
            except JCC.ChunkingError as e:
                failed_files.append(str(file) + ": " + str(e))
            # JCC.iterate(tree)
        else:
            failed_files.append(str(file) + ", has no tree!")

#    for chunk in chunks:
#       print(chunk)
    if len(failed_files):
        print("\nFiles that were not processed:")
        for file in failed_files:
            print(file)

