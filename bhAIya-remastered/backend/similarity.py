import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sys
from dotenv import load_dotenv
from utils import curl_request_embed
import os
import redis

redis_client_1=redis.Redis(host=os.getenv("REDIS_HOST"),port=os.getenv("REDIS_PORT"),db=1)
redis_client_2 = redis.Redis(
    host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=2
)
redis_client_3 = redis.Redis(
    host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=3
)
redis_client_4 = redis.Redis(
    host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=4
)

load_dotenv()


def adjust_weights(data, main_weight=0.1, sub_weight=0.25, additional_weight=0.65):
    weights = np.array([main_weight, sub_weight, additional_weight])
    categories = np.array(["Main category", "Sub categories", "Additional details"])

    # Redistribute weights for empty categories
    for i, category in enumerate(categories):
        if data[category]==[]:
            weights[(i + 1) % 3] += weights[i] / 2
            weights[(i + 2) % 3] += weights[i] / 2
            weights[i] = 0

    # Normalize weights to ensure they sum to 1
    total = np.sum(weights)
    if total > 0:
        weights = [w / total for w in weights]
    else:
        # If all weights are 0, distribute evenly
        weights = [1 / 3, 1 / 3, 1 / 3]

    return weights[0], weights[1], weights[2]

def update_embedding_cache(redis_client,key,embedding):
    embedding=embedding
    if isinstance(key, str):
        key = key.lower()
    try:
        embedding=np.array(embedding).tobytes()
        redis_client.set(key,embedding)
        # print("Embedding cache updated")
    except Exception as e:
        print(f"Error in updating embedding cache: {e}")
        pass


def get_embedding_cache(redis_client,key):
    if(isinstance(key,str)):
        key=key.lower()
    res=np.array([])
    if(redis_client.exists(key)):
        res=redis_client.get(key)
        # print("fetching from cache")
        res=np.frombuffer(res,dtype=np.float64)
    return res


def sentence_vector(sentence,redis_client,id=None):
    embedding_json=None
    embeddings=[]
    if(id!=None):
        embedding_database=get_embedding_cache(redis_client,id)
        if(embedding_database.size!=0):
            return embedding_database
    for word in sentence:
        word=word.lower()
        res=get_embedding_cache(redis_client_1,word)
        if(res.size!=0):
            embeddings.append(res)
        else:
            try:
                embedding_json = curl_request_embed(
                    f"{os.getenv('OLLAMA_URL_SERVER')}/api/embed",
                    data={"model": os.getenv("EMBEDDING_MODEL"), "input": [word]}
                )
                try:
                    embeds=embedding_json["embeddings"][0]
                except Exception as e:
                    print(f"list not there: {e}")
                    # embeds=np.zeros(384)
                    embeds=np.zeros(1024)
                    print(embedding_json)
                    sys.exit()
                if(embeds!=np.nan):
                    embeddings.append(embeds)
                else:
                    # embeds = np.zeros(384)
                    embeds = np.zeros(1024)
                    embeddings.append(embeds)
                update_embedding_cache(redis_client_1,word, embeds)
            except Exception as e:
                print(f"Error in generating embedding: {e}")
    if(id!=None):
        if(get_embedding_cache(redis_client,id).size==0):
            mean = np.mean(embeddings, axis=0)
            update_embedding_cache(redis_client,id,mean)
            return mean
    return np.mean(embeddings,axis=0)


def compute_similarity(text1, text2,redis_client,id=None):
    res = 0
    if(text1==[] or text2==[]):
        return res
    vec1 = sentence_vector(text1,redis_client_1)
    vec2 = sentence_vector(text2,redis_client,id)
    try:
        res=cosine_similarity(vec1.reshape(1,-1), vec2.reshape(1,-1))[0][0]
    except Exception as e:
        print(f"Error in computing similarity: {e}")
        pass
    return res

def weighted_average_similarity(main_similarity, sub_similarity,additional_similarity, main_weight=0.1, sub_weight=0.25, additional_weight=0.65):
    assert main_weight + sub_weight + additional_weight == 1, "Weights should sum to 1"

    return main_weight * main_similarity + sub_weight * sub_similarity + additional_weight * additional_similarity

def find_top_k_similar(match_data, data_list, top_k=3):
    match_main = match_data["Main category"]
    match_sub = match_data["Sub categories"]
    match_additional = match_data["Additional details"]

    # similarities = np.array([])
    similarities=[]
    min_similarity=np.inf

    for data in data_list:
        main_weight, sub_weight, additional_weight = adjust_weights(data)
        main_similarity = compute_similarity(match_main, data["Main category"],redis_client_2,data["id"])
        sub_similarity = compute_similarity(match_sub, data["Sub categories"],redis_client_3,data["id"])
        additional_similarity = compute_similarity(
            match_additional, data["Additional details"], redis_client_4, data["id"]
        )
        weighted_similarity = weighted_average_similarity(
            main_similarity, sub_similarity, additional_similarity,main_weight=main_weight,sub_weight=sub_weight,additional_weight=additional_weight
        )
        # similarities.append((weighted_similarity, data))
        # if(similarities.size<top_k):
        if(len(similarities)<top_k):
            #     # similarities=np.append(similarities,np.array([weighted_similarity,data]))
            if weighted_similarity < min_similarity:
                min_similarity = weighted_similarity
            similarities.append((weighted_similarity, data))
        else:
            if(weighted_similarity>min_similarity):
                # print(similarities)
                min_index=np.argmin([t[0] for t in similarities],axis=0)
                similarities[min_index]=(weighted_similarity,data)
                min_similarity = min([t[0] for t in similarities])

    # Sort by similarity in descending order and get the top K
    # similarities.sort(reverse=True, key=lambda x: x[0])
    # print(similarities)

    # return [item[1] for item in similarities[:top_k]]
    # return similarities[:top_k]
    print(similarities)
    return similarities


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
