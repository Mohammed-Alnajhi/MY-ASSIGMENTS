import csv
import numpy as np
import pickle



articles = []

with open("articles.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        articles.append({
            "id": row["id"],
            "title": row["title"],
            "content": row["content"]
        })



def clean_text(text):
    text = text.lower()
    
    cleaned = ""
    for char in text:
        if char.isalpha() or char.isspace():
            cleaned += char
    
    words = cleaned.split()
    return words



vocabulary = set()

for article in articles:
    words = clean_text(article["content"])
    vocabulary.update(words)

vocabulary = list(vocabulary)


article_vectors = []

for article in articles:
    words = clean_text(article["content"])
    vector = []
    
    for word in vocabulary:
        if word in words:
            vector.append(1)
        else:
            vector.append(0)
    
    article_vectors.append(vector)

article_vectors = np.array(article_vectors)



num_articles = len(article_vectors)

similarity_matrix = np.zeros((num_articles, num_articles))

for i in range(num_articles):
    for j in range(num_articles):
        
        dot_product = np.dot(article_vectors[i], article_vectors[j])
        norm_i = np.linalg.norm(article_vectors[i])
        norm_j = np.linalg.norm(article_vectors[j])
        
        if norm_i != 0 and norm_j != 0:
            similarity = dot_product / (norm_i * norm_j)
        else:
            similarity = 0
        
        similarity_matrix[i][j] = similarity


with open("similarities.pkl", "wb") as f:
    pickle.dump(similarity_matrix, f)



def get_top_similar(article_id):
    
    index = None
    
    for i, article in enumerate(articles):
        if article["id"] == str(article_id):
            index = i
            break
    
    if index is None:
        return "Article not found"
    
    similarities = similarity_matrix[index]
    
    similarity_pairs = list(enumerate(similarities))
    similarity_pairs = sorted(similarity_pairs, key=lambda x: x[1], reverse=True)
    
    top_3 = []
    
    for i, sim in similarity_pairs:
        if i != index:
            top_3.append(articles[i]["title"])
        if len(top_3) == 3:
            break
    
    return top_3