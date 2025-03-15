import re
import math
from collections import Counter, defaultdict

# Retrieve text content from a specified file
def fetch_text(file_location):
    with open(file_location, 'r', encoding='utf-8') as f:
        return f.read()

# Save provided data into a file
def save_text(file_location, data):
    with open(file_location, 'w', encoding='utf-8') as f:
        f.write(data)

# Process text by cleaning, removing stopwords, and stemming
def prepare_text(original_text, stop_list):
    # Remove URLs first
    text = re.sub(r'https?://\S+', '', original_text)
    # Keep only alphanumeric characters, underscores, and spaces
    text = re.sub(r'[^\w\s]', '', text)
    # Normalize multiple spaces to a single space and trim
    text = re.sub(r'\s+', ' ', text.strip())
    # Convert to lowercase
    text = text.lower()
    
    # Split into words and remove stopwords
    tokens = [token for token in text.split() if token not in stop_list]
    
    # Apply stemming rules to each word (unconditional like Ayush)
    reduced = []
    for token in tokens:
        if token.endswith('ing'):
            # Remove 'ing' without length check
            reduced.append(token[:-3])
        elif token.endswith('ly'):
            # Remove 'ly' without length check
            reduced.append(token[:-2])
        elif token.endswith('ment'):
            # Remove 'ment' without length check
            reduced.append(token[:-4])
        else:
            # Keep word unchanged if no suffix matches
            reduced.append(token)
    
    # Join stemmed words back into a string
    return ' '.join(reduced)

# Calculate term frequency for each word in the text
def calculate_tf(text_data):
    # Split text into words
    terms = text_data.split()
    # Return empty dict if no words
    if not terms:
        return {}
    # Count occurrences of each word
    term_counts = Counter(terms)
    # Total number of words
    total_terms = len(terms)
    # Compute TF as count divided by total
    return {term: count / total_terms for term, count in term_counts.items()}

# Determine inverse document frequency for words across texts
def calculate_idf(all_texts):
    # Get total number of documents
    num_texts = len(all_texts)
    # Initialize dict to track term presence across docs
    term_presence = defaultdict(int)
    # Iterate through each document
    for text in all_texts:
        # Get unique terms in this document
        unique_terms = set(text.split())
        # Increment count for each term
        for term in unique_terms:
            term_presence[term] += 1
    # Compute IDF
    return {term: math.log(num_texts / count) + 1 for term, count in term_presence.items()}

# Compute TF-IDF scores for words based on TF and IDF
def calculate_tfidf(tf_scores, idf_scores):
    # Compute TF-IDF for all terms, default IDF to 0, round to 2 decimals
    tfidf_values = {term: round(tf_scores[term] * idf_scores.get(term, 0), 2) for term in tf_scores}
    # Return the TF-IDF dict
    return tfidf_values

# Pick the top 5 words by TF-IDF score, sorted appropriately
def select_top_words(tfidf_dict):
    # Sort by descending score, then alphabetically by term
    ranked = sorted(tfidf_dict.items(), key=lambda item: (-item[1], item[0]))
    # Return top 5 items
    return ranked[:5]

# Handle document processing and TF-IDF computation
def process_documents():
    # Load document list from file
    doc_list = fetch_text('tfidf_docs.txt').splitlines()
    
    # Load stopwords from file
    stop_words = set(fetch_text('stopwords.txt').splitlines())
    
    # Initialize dict to store processed texts
    processed_texts = {}
    # Process each document in the list
    for doc_name in doc_list:
        # Remove any trailing/leading whitespace from filename
        doc_name = doc_name.strip()
        # Read raw content from document
        raw_content = fetch_text(doc_name)
        # Preprocess the content
        processed_content = prepare_text(raw_content, stop_words)
        # Store processed text
        processed_texts[doc_name] = processed_content
        # Save preprocessed text to file
        save_text(f'preproc_{doc_name}', processed_content)
    
    # Calculate IDF values across all processed texts
    idf_values = calculate_idf(processed_texts.values())
    
    # Compute and save TF-IDF for each document
    for doc_name, processed_content in processed_texts.items():
        # Calculate term frequencies
        tf_values = calculate_tf(processed_content)
        # Compute TF-IDF scores
        tfidf_scores = calculate_tfidf(tf_values, idf_values)
        # Get top 5 words by TF-IDF
        top_words = select_top_words(tfidf_scores)
        # Format output as a single-line list of tuples
        formatted_output = '[' + ', '.join(f"('{word}', {score:.2f})" for word, score in top_words) + ']'
        # Save TF-IDF output to file
        save_text(f'tfidf_{doc_name}', formatted_output)

# Execute the document processing directly
process_documents()