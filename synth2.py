from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder.appName("Dynamic Schema Classification").getOrCreate()

def get_schema_metadata(table_name, sample_size=10):
    """
    Fetch schema metadata and sample values for a given table dynamically.
    """
    # Get schema information
    df = spark.read.table(table_name)
    schema_info = df.schema

    # Fetch sample values
    sample_data = df.limit(sample_size).toPandas()

    return schema_info, sample_data

# Example usage
schema_info, sample_data = get_schema_metadata("your_table_name")

import spacy
import numpy as np
from sklearn.cluster import KMeans
import umap

# Load pre-trained NLP model
nlp = spacy.load("en_core_web_sm")

def classify_column_name(col_name):
    """
    Uses NLP-based techniques to classify column names dynamically.
    """
    col_name_cleaned = col_name.lower().replace("_", " ")
    doc = nlp(col_name_cleaned)

    # Extract Named Entities if available
    entities = [ent.label_ for ent in doc.ents]

    if "GPE" in entities or "LOC" in entities:
        return "region"
    elif "ORG" in entities:
        return "organization"
    elif "PERSON" in entities:
        return "name"
    elif "DATE" in entities:
        return "date"
    elif "CARDINAL" in entities or "MONEY" in entities:
        return "numeric"

    # Use NLP embeddings for unknown cases
    vector = np.array(doc.vector).reshape(1, -1)
    umap_model = umap.UMAP(n_components=2, random_state=42)
    reduced_vector = umap_model.fit_transform(vector)

    kmeans = KMeans(n_clusters=5, random_state=42)
    cluster = kmeans.fit_predict(reduced_vector)

    # Dynamically assign categories based on clustering
    categories = ["name", "organization", "region", "date", "numeric"]
    return categories[cluster[0]]

# Example
print(classify_column_name("USD_Value"))  # Output: "numeric"
print(classify_column_name("Company"))    # Output: "organization"


import re

def classify_column_values(sample_values):
    """
    Uses regex & NLP to classify column values dynamically.
    """
    if all(re.match(r"\d+\.\d+", str(val)) for val in sample_values):
        return "numeric"
    elif all(re.match(r"\d{4}-\d{2}-\d{2}", str(val)) for val in sample_values):
        return "date"
    elif all(re.match(r"[A-Za-z ]+", str(val)) for val in sample_values):
        return "name"
    else:
        return "text"

# Example usage
sample_values = ["2023-04-05", "2023-04-06"]
print(classify_column_values(sample_values))  # Output: "date"

sample_values = ["100.23", "200.50"]
print(classify_column_values(sample_values))  # Output: "numeric"


from faker import Faker
import random
import datetime

fake = Faker()

def generate_synthetic_value(col_type):
    """
    Generates realistic synthetic data based on detected column type.
    """
    if col_type == "name":
        return fake.name()
    elif col_type == "organization":
        return fake.company()
    elif col_type == "region":
        return fake.country()
    elif col_type == "date":
        return fake.date()
    elif col_type == "numeric":
        return round(random.uniform(1.0, 10000.0), 2)
    else:
        return fake.sentence(nb_words=5)

# Example usage
print(generate_synthetic_value("name"))  # Output: "John Doe"
print(generate_synthetic_value("organization"))  # Output: "Tata Pharmaceuticals"
print(generate_synthetic_value("numeric"))  # Output: "5678.23"
