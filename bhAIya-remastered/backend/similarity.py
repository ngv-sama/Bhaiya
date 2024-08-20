import numpy as np
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from Levenshtein import distance
import sys
import requests
from dotenv import load_dotenv
from utils import perform_request
import os
import redis
import pickle

redis_client=redis.Redis(host=os.getenv("REDIS_HOST"),port=os.getenv("REDIS_PORT"),db=1)

load_dotenv()

def update_embedding_cache(key,embedding):
    embedding=embedding
    try:
        embedding=pickle.dumps(embedding)
        redis_client.set(key.lower(),embedding)
        print("Embedding cache updated")
    except Exception as e:
        print(f"Error in updating embedding cache: {e}")
        pass


def get_embedding_cache(key):
    key=key.lower()
    res=None
    if(redis_client.exists(key)):
        res=redis_client.get(key)
        print("fetching from cache")
        res=pickle.loads(res)
    return res


def sentence_vector(sentence):
    # words = [word for word in sentence if word in model.wv]
    # if not words:
    #     return np.zeros(model.vector_size)
    # return np.mean(model.wv[words], axis=0)
    embedding_json=None
    embeddings=[]
    for word in sentence:
        res=get_embedding_cache(word)
        if(res!=None):
            embeddings.append(res)
        else:
            try:
                embedding_json=requests.post(f"{os.getenv('OLLAMA_URL_SERVER')}/api/embed",json={"model":os.getenv("EMBEDDING_MODEL"),"input":word}).json()
                embeds=embedding_json["embeddings"][0]
                if(embeds!=np.nan):
                    embeddings.append(embeds)
                else:
                    print("ISNAN")
                    print(word)
                    sys.exit()
                    embeds = np.zeros(1024)
                    embeddings.append(embeds)
                update_embedding_cache(word, embeds)
            except Exception as e:
                print(f"Error in generating embedding: {e}")
    return np.mean(embeddings,axis=0)

def compute_similarity(text1, text2):
    vec1 = sentence_vector(text1)
    vec2 = sentence_vector(text2)
    # print(vec1)
    # print(vec2)
    # sys.exit()
    # return cosine_similarity([vec1], [vec2])[0][0]
    res=0
    try:
        res=cosine_similarity(vec1.reshape(1,-1), vec2.reshape(1,-1))[0][0]
    except Exception as e:
        print(f"Error in computing similarity: {e}")
        pass
    return res

def weighted_average_similarity(main_similarity, sub_similarity,additional_similarity, main_weight=0.2, sub_weight=0.4, additional_weight=0.4):
    assert main_weight + sub_weight + additional_weight == 1, "Weights should sum to 1"

    return main_weight * main_similarity + sub_weight * sub_similarity + additional_weight * additional_similarity

def find_top_k_similar(match_data, data_list, top_k=3):
    # Word2Vec model
    sentences = [item["Main category"] + item["Sub categories"]+ item["Additional details"] for item in data_list]
    # model = train_word2vec_model(sentences)

    match_main = match_data["Main category"]
    match_sub = match_data["Sub categories"]
    match_additional = match_data["Additional details"]

    similarities = []

    for data in data_list:
        main_similarity = compute_similarity(match_main, data["Main category"])
        sub_similarity = compute_similarity(match_sub, data["Sub categories"])
        additional_similarity = compute_similarity(
            match_additional, data["Additional details"]
        )
        weighted_similarity = weighted_average_similarity(
            main_similarity, sub_similarity, additional_similarity
        )
        similarities.append((weighted_similarity, data))

    # Sort by similarity in descending order and get the top K
    similarities.sort(reverse=True, key=lambda x: x[0])
    # print(similarities)

    # return [item[1] for item in similarities[:top_k]]
    return similarities[:top_k]


if __name__ == "__main__":

    # Sample data
    data_list = [
        {"id":452,"Main category": ["banana", "cherry", "date"], "Sub categories": ["elephant", "frog", "goat"],"Additional details": ["Summer", "red", "fruit", "Party"] },
        {"id":532,"Main category": ["sports", "clothes", "football"], "Sub categories": ["blue", "shirt", "large"],"Additional details": ["Summer 2012.0", "Blue", "Casual", "Party"]},
        {"id":876,"Main category": ["blue", "shirt", "large"], "Sub categories":["Summer 2012.0", "Blue", "Casual", "Party"],"Additional details": ["sports", "clothes", "football"] },
        {"id":457,"Main category": ["cherry", "date", "fig"], "Sub categories": ["frog", "goat", "horse"],"Additional details": ["winter", "brown"]},
        {"id":435,"Main category": ["apple", "blueberry", "cherry"], "Sub categories": ["ant", "bat", "cat"],"Additional details": ["Summer", "cherry", "fruit", "home"]},
    ]


    # match_data = {"Main category": ["apple", "banana", "cherry"], "Sub categories": ["dog", "elephant", "frog"]}
    match_data = {"Main category": ["clothes", "t-shirt","Mens fashion"], "Sub categories": ["deep blue", "big"], "Additional details": ["sports","cricket"]}

    # Prepare sentences for training the Word2Vec model

    # Find top 3 similar items
    top_k_similar = find_top_k_similar(match_data, data_list, top_k=2)
    print("\n\n",top_k_similar)
