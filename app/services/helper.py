import re

def extract_text_from_tool_content(content: str) -> str:
    # find the first text='....' inside the mess
    match = re.search(r"text='(.*?)', type='output_text'", content, re.DOTALL)
    if match:
        extracted = match.group(1)
        # unescape escaped newlines and quotes
        extracted = extracted.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"')
        return extracted.strip()
    else:
        return ""

def reconstruct_tool_call(buffer):
    args_pieces = []
    id_ = None
    name = None
    
    for chunk in buffer:
        tool_call = chunk.tool_calls[0]
        id_ = id_ or tool_call.get("id")
        name = name or tool_call.get("name")
        
        arg_piece = ""
        if tool_call.get("args"):
            arg_piece = tool_call["args"]
        elif "function" in tool_call and "arguments" in tool_call["function"]:
            arg_piece = tool_call["function"]["arguments"]
        
        args_pieces.append(arg_piece)
    
    full_args = "".join(args_pieces)
    
    return {
        "id": id_,
        "name": name,
        "args": full_args
    }