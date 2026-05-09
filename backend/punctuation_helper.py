import re

def preserve_and_process(text, process_word_func):
    """
    Process text while preserving punctuation.
    
    Args:
        text: Input text with punctuation
        process_word_func: Function to process individual words (without punctuation)
    
    Returns:
        Processed text with punctuation preserved in original positions
    """
    # Split on spaces while keeping track of words and trailing punctuation
    # Pattern: match one or more non-space chars, optionally followed by punctuation
    words_and_punct = re.findall(r'[^\s]+', text)
    
    processed = []
    for word_with_punct in words_and_punct:
        # Separate letters from trailing punctuation
        # Match: leading content (letters/text), then trailing punctuation
        match = re.match(r'^([a-zA-Z0-9ĕăâêôơưđàáảãạăằắẳẵặâầấẩẫậêềếểễệơờớởỡợưừứửữựì-ỵ]+)(.*?)$', word_with_punct, re.IGNORECASE)
        
        if match:
            word = match.group(1)
            trailing_punct = match.group(2)
        else:
            # No letters found, keep as is
            processed.append(word_with_punct)
            continue
        
        # Process the word
        processed_word = process_word_func(word)
        
        # Reattach trailing punctuation
        processed.append(processed_word + trailing_punct)
    
    return ' '.join(processed)
