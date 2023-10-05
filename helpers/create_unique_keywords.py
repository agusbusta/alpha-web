import json

def extract_unique_words(input_file):
    unique_words = set()
    with open(input_file, 'r') as file:
        for line in file:
            words = line.split()
            for word in words:
                # Remove punctuation and convert to lowercase
                cleaned_word = word.strip('.,!?()[]{}":;')
                cleaned_word = cleaned_word.lower()
                unique_words.add(cleaned_word)
    return list(unique_words)

input_file_path = r'helpers\raw_keywords.text'
output_file_path = 'unique_keywords.json'
unique_words_list = extract_unique_words(input_file_path)

with open(output_file_path, 'w') as json_file:
    json.dump(unique_words_list, json_file, indent=4)

print(f'Unique words extracted and saved to {output_file_path}')