from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a subprocess of a python file and prints out: If the process_return code is not 0, 'Process exited with code X'. If there was no STDOUT or STDERR it returns 'No output produced', otherwise it prints the STDOUT and STDERR",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative file path from the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Any arguments that are to be passed to the python file",
                items=types.Schema(type=types.Type.STRING, description="Argument as a string"),     
            ),
            
        },
    ),
)

schema_get_file_content= types.FunctionDeclaration(
    name="get_file_content",
    description="Attempts to read a file and returns the content; if the file is over 10000 characters it truncates it to 10000 characters.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative file path from the working directory",
            ),
            
        },
    ),
)


schema_write_file= types.FunctionDeclaration(
    name="write_file",
    description="Attempts to write to a file; if it doesnt exist it creates it and proceed to writing the content of the document and saving it, if it exists it will overwrite the content of the document and save it.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative file path from the working directory",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to file.",
            ),
        },
    ),
)

