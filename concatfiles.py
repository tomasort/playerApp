import os
import sys

def append_contents(output_file, path, indent=""):
    """
    Recursively appends the contents of all files and directories in the given path 
    to the output file, formatted in Markdown.

    :param output_file: File object for the output file.
    :param path: Current directory or file path.
    :param indent: Indentation for Markdown formatting.
    """
    if os.path.isdir(path):
        # Write directory name
        directory_name = os.path.basename(path)
        ignore = ['git', 'zillow_html', 'venv', 'pycache']
        for d in ignore:
            if d in directory_name:
                return
        output_file.write(f"{indent}# Directory: `{directory_name}`\n\n")

        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            # Recursively append contents of files and directories
            append_contents(output_file, file_path, indent + "#")
        output_file.write(f"{indent}# End of Directory `{directory_name}`\n\n")
    elif os.path.isfile(path):
        # Write file name and contents
        file_name = os.path.basename(path)
        print(file_name)
        ignore = ["DS_Store", "sql", ".ico", ".svg", ".eot"]
        for f in ignore:
            if f in file_name:
                return
        output_file.write(f"{indent}# File: `{file_name}`\n")
        output_file.write(f"```\n")

        with open(path, 'r') as infile:
            contents = infile.read()
        output_file.write(contents)
        output_file.write(f"\n```\n\n")

def append_files_in_directory(directory_path, output_file):
    """
    Appends the contents of all files and directories in the given directory 
    to a single file, preceded by the file or directory name in Markdown format.

    :param directory_path: Path to the directory containing files and directories.
    :param output_file: Path to the output file.
    """
    with open(output_file, 'w') as outfile:
        append_contents(outfile, directory_path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py [directory_path] [output_file]")
        sys.exit(1)

    directory_path = sys.argv[1]
    output_file = sys.argv[2]
    append_files_in_directory(directory_path, output_file)
