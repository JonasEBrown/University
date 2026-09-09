import os
import sys

def process_file(path: str) -> tuple[list[str], list[str], list[str]]:
    """
        Process a Python file to extract imports, type definitions, and code.

        Args:
            path (str): The path to the Python file.

        Returns:
            tuple[list[str], list[str], list[str]]: A tuple containing lists of imports, type definitions, and code.
    """
    imports, types, lines = [], [], [] # Lists to hold different parts of the file.
    with open(path, 'r') as file: # Open the file for reading.
        read = file.readlines() # Read all lines in the file.
        for index, line in enumerate(read): # Iterate over each line.
            if index < len(read) - 1: # If not the last line in the file:
                nextLine = read[index + 1].strip()
                if line == "\n" and not(nextLine.startswith("def") or nextLine.startswith("class") or nextLine.startswith("@")):
                    continue # Skip empty lines if they don't seperate the next function or class.
            split = line.split(' ') # Split the line into words.
            match split[0]: # Check the first word to categorise the line.
                case "from" | "import": # If it's an import statement:
                    # If it's a local import or the package itself, skip it.
                    if not split[1].startswith('.') and split[1] != "case_study":
                        imports.append(line.strip()) # Add to imports list.
                case "type": # If it's a type definition:
                    types.append(line.strip()) # Add to types list.
                case _: # Else it's regular code:
                    lines.append(line) # Add to code list.
    lines.append('\n')
    return imports, types, lines # Return the categorised lists.

def condense_module_to_file(module_path: str | None = None, output_file: str = "output.py"):
    """
        Condense all Python files in a folder into a single output file.

        Args:
            module_path (str | None): The path to the module directory. If None, uses the parent directory of the current script.
            output_file (str): The path to the output file.
    """
    with open(output_file, 'w') as file: # Open the output file for writing.
        file.write( # Write the content to the output file.
            '\n\n'.join([ # Join different sections with double newlines.
                (
                    lambda x: '\n'.join( # If index < 2, remove duplicates, sort by length, and join with newlines excluding comments.
                        sorted(set(x), key=lambda line: len(line.split('#')[0]))
                    ) if index < 2 else ''.join(x) # else just join with no separator.
                )([ # Process each category (imports, types, code).
                    item
                    for file in category
                    for item in file
                ])
                for index, category in enumerate(zip(*[ # Transpose the list of tuples from
                    # [(imports1, types1, code1), (imports2, types2, code2), ...]
                    # to [(imports1, imports2, ...), (types1, types2, ...), (code1, code2, ...)].
                    process_file(f"{dirpath}\\{filename}") # Process each Python file.
                    for (dirpath, _, filenames) in os.walk(
                        module_path if type(module_path) is str else '\\'.join(
                            sys.path[0].split('\\')[:-1] # Get parent directory of current script.
                        ) # Use provided module path or parent directory of current script.
                    ) # Walk through the directory.
                    for filename in filenames # Process each Python file in the directory.
                    if not dirpath.endswith("__pycache__") # Ignore cache directories.
                    if not __file__.endswith(filename) # Ignore this script file.
                    if not filename.startswith('_') # Ignore private modules.
                ]))
            ])
        )

if __name__ == "__main__": # If this script is run directly:
    condense_module_to_file() # Run the condensing function with default parameters.