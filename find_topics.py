from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
df_top_emb = pd.read_pickle('static/df_top_emb')


def my_find_topics(search_term, top_n=5):

    search_embedding = embedding_model.encode([search_term], show_progress_bar=False).flatten()

    sims = cosine_similarity(search_embedding.reshape(1, -1), df_top_emb.topic_embedding.to_list()).flatten()

    ids = np.argsort(sims)[-top_n:]
    similarity = [sims[i] for i in ids][::-1]
    similar_topics = [df_top_emb.topic_id.to_list()[index] for index in ids][::-1]

    return similar_topics, similarity


def my_get_keywords(topic_id):

    return df_top_emb[df_top_emb['topic_id'] == topic_id].keywords.to_list()[0]
