from redisvl.extensions.cache.llm import SemanticCache
from redisvl.utils.vectorize import HFTextVectorizer
from redisvl.extensions.cache.embeddings import EmbeddingsCache
from redis_server import r
import pandas as pd

langcache_embed = HFTextVectorizer(
    model="redis/langcache-embed-v1",
    cache=EmbeddingsCache(redis_client=r, ttl=3600)
)

llmcache = SemanticCache(
    name="llmcache",
    vectorizer=langcache_embed,
    redis_client=r,
    distance_threshold=0.3
)

class SemCache:

    def __init__(self, embedding_model: HFTextVectorizer, cache: SemanticCache):
        self.embedding_model = embedding_model
        self.cache = cache

    def build_cache(self, df: pd.DataFrame, clear_cache: bool):

        if clear_cache:
            self.cache.clear()

        for i in range(len(df)):
            self.cache.store(
                prompt=df.iloc[i]["question"],
                response=df.iloc[i]["response"]
            )
        
        print("Cache built.")

    def clear_cache(self):

        self.cache.clear()

        print("Cache cleared.")

    def check_cache(self, question: str):

        if response := self.cache.check(prompt=question):
            # print(response)
            # [{
            #     'entry_id': 'c1a2be958744600f5c5d99d155c75ca1a231eae4b8e089587a26a35c6b30b391', 
            #     'prompt': 'What is a VPN?', 
            #     'response': 'A Virtual Private Network creates a secure, encrypted connection over a less secure network like the internet.', 
            #     'vector_distance': 0.144856154919, 
            #     'inserted_at': 1767512524.36, 
            #     'updated_at': 1767512524.36, 
            #     'key': 'llmcache:c1a2be958744600f5c5d99d155c75ca1a231eae4b8e089587a26a35c6b30b391'
            # }]
            return response
        else:
            print("Empty cache")
            return "Empty cache"

cache = SemCache(langcache_embed, llmcache)

if __name__ == "__main__":

    llmcache.clear()

    # Data containing IT questions and answers
    df = pd.DataFrame({
        "question": [
            "What is the purpose of a Firewall?",
            "What does DNS stand for and what is its function?",
            "What is the difference between RAM and ROM?",
            "What is a VPN?",
            "Define DHCP and its role in networking.",
            "What is the 'Blue Screen of Death' (BSOD)?",
            "What are the seven layers of the OSI model?",
            "Explain the difference between TCP and UDP.",
            "What is Active Directory?",
            "What is the primary function of a Router?"
        ],
        "response": [
            "A security system that monitors and controls incoming and outgoing network traffic based on predefined rules.",
            "Domain Name System; it translates human-readable domain names (like google.com) into IP addresses.",
            "RAM is volatile short-term memory for active data, while ROM is non-volatile permanent storage for firmware.",
            "A Virtual Private Network creates a secure, encrypted connection over a less secure network like the internet.",
            "Dynamic Host Configuration Protocol; it automatically assigns IP addresses to devices on a network.",
            "A critical system error in Windows that causes the computer to freeze or restart to prevent damage.",
            "Physical, Data Link, Network, Transport, Session, Presentation, and Application layers.",
            "TCP is connection-oriented and reliable (guarantees delivery), while UDP is connectionless and faster.",
            "A Microsoft service used to manage users, computers, and permissions within a Windows domain network.",
            "A networking device that forwards data packets between different computer networks."
        ]
    })

    for i in range(len(df)):
        llmcache.store(
            prompt=df.iloc[i]["question"],
            response=df.iloc[i]["response"]
        )
    
    question = "Talk about VPN"
    if response := llmcache.check(prompt=question):
        print(response)
    else:
        print("Empty cache")