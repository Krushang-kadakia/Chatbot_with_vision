import base64
import binascii
import ollama
import fitz  # PyMuPDF

import hashlib

_PDF_CACHE = {}

def process_input_data(input_data):
    """
    Process input data (bytes) and return a list of image bytes.
    - If PDF: Convert each page to an image (PNG bytes). Uses hashing to cache results.
    - If Image: Return as a single-item list of bytes.
    """
    processed_images = []
    
    is_pdf = False
    if isinstance(input_data, bytes) and input_data.startswith(b'%PDF'):
        is_pdf = True
    
    if is_pdf:
        # Generate hash of input bytes for caching
        file_hash = hashlib.md5(input_data).hexdigest()
        if file_hash in _PDF_CACHE:
            print(f"DEBUG Logic: Returning cached PDF pages for hash {file_hash}")
            return _PDF_CACHE[file_hash]

        try:
            print("DEBUG Logic: Detected PDF input. Converting pages to images...")
            doc = fitz.open(stream=input_data, filetype="pdf")
            for i, page in enumerate(doc):
                pix = page.get_pixmap(matrix=fitz.Matrix(1, 1)) 
                img_bytes = pix.tobytes("png")
                processed_images.append(img_bytes)
            print(f"DEBUG Logic: Converted PDF to {len(processed_images)} images.")
            
            # Store in cache
            _PDF_CACHE[file_hash] = processed_images
        except Exception as e:
            print(f"DEBUG Logic: Error processing PDF: {e}")
            processed_images.append(input_data)
    else:
        # Assume it's an image
        print("DEBUG Logic: Detected Image input.")
        processed_images.append(input_data)
        
    return processed_images

def chat_with_model(messages, model='qwen2.5vl:7b'):
    """
    Chat with the Ollama model with Vision Context Management.
    Prevents GGML assertion errors by limiting visual tokens.
    """
    try:
        # Prepare messages for Ollama
        api_messages = []
        for i, m in enumerate(messages):
            msg = {'role': m['role'], 'content': m['content']}
            
            # --- VISION CONTEXT MANAGEMENT ---
            # Rule: Only send images for the current (last) user message.
            # Ollama's vision encoder can crash if too many images accumulate in history.
            is_last_message = (i == len(messages) - 1)
            
            if is_last_message and 'images' in m and m['images']:
                all_images_for_msg = []
                for img in m['images']:
                    # Decode if base64 string
                    img_bytes = None
                    if isinstance(img, str):
                        try:
                            img_bytes = base64.b64decode(img)
                        except binascii.Error:
                            img_bytes = img
                    else:
                        img_bytes = img
                    
                    if isinstance(img_bytes, bytes):
                        # PDF/Image Processing
                        images_from_file = process_input_data(img_bytes)
                        # LIMIT: Only send first 10 pages/images if PDF is huge
                        all_images_for_msg.extend(images_from_file[:10]) 
                    else:
                        all_images_for_msg.append(img)
                
                msg['images'] = all_images_for_msg
                print(f"DEBUG Logic: Sending {len(msg['images'])} images for current turn.")
            
            api_messages.append(msg)

        # Increase context size and set num_thread for multi-modal stability
        stream = ollama.chat(
            model=model,
            messages=api_messages,
            options={
                'num_thread': 8,
                'num_ctx': 8192, # Increased context for combined text+vision tokens
                'temperature': 0.7
            },
            stream=True,
        )
        
        for chunk in stream:
            if 'message' in chunk and 'content' in chunk['message']:
                yield chunk['message']['content']
                
    except Exception as e:
        yield f"Error: {str(e)}"
