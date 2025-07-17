import os
from resources.config import MAX_CHARS
import subprocess
from google.genai import types

def print_directory_content(dir,file_path):
    package = []
    for item in dir:
        try:
            item_path = os.path.join(file_path, item)
            package.append(f'- {item}: file_size={os.path.getsize(item_path)} bytes, is_dir={os.path.isdir(item_path)}')
        except Exception as e:
            return f'Error: {e}'
    return package

def path_security(working_directory, directory):
    full_path = os.path.join(working_directory, directory)
    dirc1 = os.path.abspath(full_path)
    working_dir_allowed = os.path.abspath(working_directory)

    if not dirc1.startswith(working_dir_allowed):
        return full_path, 1

    return full_path, 0
 
def get_files_info(working_directory, directory="."):
    full_path, status = path_security(working_directory, directory)
    
    if status == 1:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not os.path.isdir(full_path):
        return f'Error: "{directory}" is not a directory'
    
    dir_list = os.listdir(full_path)
    return print_directory_content(dir_list, full_path)
    
def get_file_content(working_directory, file_path):
    full_path, status = path_security(working_directory, file_path)
    
    if status == 1:
        return f'Error: Cannot list "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(full_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    content = ''

    with open(full_path) as file:
        try:
            content = file.read()
            return content[:MAX_CHARS] + f"[...File {full_path} truncated at {MAX_CHARS} characters]" if len(content) > MAX_CHARS else content
        except Exception as e:
            return f'Error: {e}'
        
    
def write_file(working_directory, file_path, content):
    full_path, status = path_security(working_directory, file_path)
    
    if status == 1:
        return full_path
    if not os.path.isfile(full_path):
        try:
            open(file=full_path, mode='x')
        except Exception as e:
            return f'Error: {e}'
        
    try:
        with open(file=full_path, mode='w') as file:
            file.write(content)
        return f'Successfully wrote to "{full_path}" ({len(content)} characters written)'
    except Exception as e:
            return f'Error: {e}'
        
def run_python_file(working_directory, file_path, args=[]):
    full_path, status = path_security(working_directory, file_path)
    
    if status == 1:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(full_path):
        return f'Error: File "{file_path}" not found.'
    
    if file_path[-3:] != ".py":
        return f'Error: "{full_path[-3:]}" is not a Python file.'
    
    try:
        command = ["python3", full_path] + args
        result = subprocess.run(args=command, timeout=30, capture_output=True)
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
    std_out = result.stdout
    std_err = result.stderr
    process_return_code = result.returncode
    
    if process_return_code != 0:
        print("Process exited with code X")
        return f"Process exited with code X"
    if std_out == None and std_err == None:
        return f"No output produced"
    
    print(f"STDOUT: {std_out}")
    print(f"STDERR: {std_err}")
    return f"STDOUT: {std_out} \n STDERR: {std_err}"


def call_function(function_call_part, verbose=False):

    function_dic = {
    "get_files_info": get_files_info,
    "run_python_file": run_python_file,
    "get_file_content": get_file_content,
    "write_file": write_file
}

    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_name = function_call_part.name
    function_args = function_call_part.args
    function_args["working_directory"] = "./calculator"

    if function_name not in function_dic:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    function_called = function_dic[function_name]
    function_result = function_called(**function_args)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
)