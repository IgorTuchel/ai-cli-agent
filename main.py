import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import sys
from resources.config import MODEL, SYSTEM_PROMPT, MAX_ITTERATIONS
from resources.schemas import *
import functions.get_files_info
import time
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_run_python_file,
        schema_get_file_content,
        schema_write_file
    ]
)

def main():
    verbose = "--verbose" in sys.argv
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I fix the calculator?"')
        sys.exit(1)

    user_prompt = " ".join(args)

    messages = [ 
        types.Content(role="user", parts=[types.Part(text=user_prompt)])
    ]
    itterations = 0
    while True:
        itterations += 1
        if itterations > MAX_ITTERATIONS:
            print(f"Maximum iterations ({MAX_ITTERATIONS}) reached.")
            sys.exit(1)
        
        try:
            final_response = generate_content(client,messages, verbose)
            if final_response:
                print("Final response:")
                print(final_response)
                break
        except Exception as e:
            if "429" in e.args[0]:
                print("Model Token Limit Reached - Exiting...")
                sys.exit(69)
            if "503" in e.args[0]:
                print("Model Overloaded - No counting itteration...")
                itterations -= 1
                time.sleep(5)
            else:
                print(f"Error in generate_content: {e}")
            
def generate_content(client, messages,verbose):
    response = client.models.generate_content(
                model=MODEL,
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions],
                    system_instruction=SYSTEM_PROMPT)
            )
    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    
    if response.candidates:
        for candidate in response.candidates:
            messages.append(candidate.content)
            
    if not response.function_calls:
        return response.text

    function_responses = []
    for function_call_part in response.function_calls:
        function_call_result = functions.get_files_info.call_function(function_call_part, verbose)

        if (
            not function_call_result.parts
            or not function_call_result.parts[0].function_response
        ):
            raise Exception("empty function call result")
        if verbose:
            print(f"-> {function_call_result.parts[0].function_response.response}")
        function_responses.append(function_call_result.parts[0])
    
    if not function_responses:
        raise Exception("no function responses generated, exiting.")

    messages.append(types.Content(role="tool", parts=function_responses))

if __name__ == "__main__":
    main()
