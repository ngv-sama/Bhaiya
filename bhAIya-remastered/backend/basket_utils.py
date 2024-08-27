import numpy as np
from dotenv import load_dotenv
import sys
from similarity import compute_similarity

load_dotenv()


def get_recommendations(data,data_list,already_bought,recommendation_count=5):
    min_similarity = np.inf
    similarities = []
    for match_data in data_list:
        if(match_data["id"] in already_bought):
            continue
        data_categories=[]
        if(match_data["Additional details"]==[]):
            if(match_data["Sub categories"]==[]):
                data_categories.extend(match_data["Main category"])
            else:
                data_categories.extend(match_data["Sub categories"])
        else:
            data_categories.extend(match_data["Additional details"])
        similarity=compute_similarity(data,data_categories)
        if len(similarities) < recommendation_count:
            #     # similarities=np.append(similarities,np.array([weighted_similarity,data]))
            if similarity < min_similarity:
                min_similarity = similarity
            similarities.append((similarity, data))
        else:
            if similarity > min_similarity:
                # print(similarities)
                min_index = np.argmin([t[0] for t in similarities], axis=0)
                similarities[min_index] = (similarity, data)
                min_similarity = min([t[0] for t in similarities])
    return similarities

if __name__ == "__main__":
    data_list = [
        {
            "id": 452,
            "Main category": ["banana", "cherry", "date"],
            "Sub categories": ["elephant", "frog", "goat"],
            "Additional details": ["Summer", "red", "fruit", "Party"],
        },
        {
            "id": 532,
            "Main category": ["sports", "clothes", "football"],
            "Sub categories": ["blue", "shirt", "large"],
            "Additional details": ["Summer 2012.0", "Blue", "Casual", "Party"],
        },
        {
            "id": 876,
            "Main category": ["blue", "shirt", "large"],
            "Sub categories": ["Summer 2012.0", "Blue", "Casual", "Party"],
            "Additional details": ["sports", "clothes", "football"],
        },
        {
            "id": 457,
            "Main category": ["cherry", "date", "fig"],
            "Sub categories": ["frog", "goat", "horse"],
            "Additional details": ["winter", "brown"],
        },
        {
            "id": 435,
            "Main category": ["apple", "blueberry", "cherry"],
            "Sub categories": ["ant", "bat", "cat"],
            "Additional details": ["Summer", "cherry", "fruit", "home"],
        },
    ]

    # match_data = {"Main category": ["apple", "banana", "cherry"], "Sub categories": ["dog", "elephant", "frog"]}
    match_data = {
        "Main category": ["clothes", "t-shirt", "Mens fashion"],
        "Sub categories": ["deep blue", "big"],
        "Additional details": ["sports", "cricket"],
    }

    # Prepare sentences for training the Word2Vec model

    # Find top 3 similar items
    top_k_similar = get_recommendations(match_data, data_list, recommendation_count=2)
    print("\n\n", top_k_similar)
