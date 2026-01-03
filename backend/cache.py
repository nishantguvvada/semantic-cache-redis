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
    distance_threshold=0.1
)

if __name__ == "__main__":

    # Data containing IT questions and answers
    df = pd.DataFrame({
        "Question": [
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
        "Answer": [
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
    
    question = "What does VPN mean?"
    if response := llmcache.check(prompt=question):
        print(response)
    else:
        print("Empty cache")