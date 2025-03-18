#pip install spacy umap-learn fuzzywuzzy gensim nltk pandas faker
#python -m spacy download en_core_web_sm


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
import pandas as pd
from sklearn.cluster import KMeans
import umap
from fuzzywuzzy import process

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def infer_column_category(col_name, existing_data=None):
    """
    Dynamically infers the column category based on NER, Clustering, and Similarity Matching.
    """
    col_name_cleaned = col_name.lower().replace("_", " ")

    # Step 1: Use Named Entity Recognition (NER)
    doc = nlp(col_name_cleaned)
    for ent in doc.ents:
        if ent.label_ in ["PERSON"]:
            return "name"
        elif ent.label_ in ["ORG"]:
            return "organization"
        elif ent.label_ in ["GPE", "LOC"]:
            return "region"
        elif ent.label_ in ["DATE", "TIME"]:
            return "date" if "date" in col_name_cleaned else "timestamp"

    # Step 2: If column is unknown, cluster it based on embeddings
    vector = np.array(doc.vector).reshape(1, -1)
    umap_model = umap.UMAP(n_components=2, random_state=42)
    reduced_vector = umap_model.fit_transform(vector)

    kmeans = KMeans(n_clusters=5, random_state=42)  # Automatically determines clusters
    cluster = kmeans.fit_predict(reduced_vector)

    # Step 3: Use Fuzzy Matching on existing column names
    if existing_data is not None:
        best_match, score = process.extractOne(col_name_cleaned, existing_data)
        if score > 80:
            return best_match  # Assign to existing known category

    return f"category_{cluster[0]}"  # Assign to dynamic category


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
from pyspark.sql import Row

fake = Faker()

def generate_dynamic_value(col_name, existing_data=None):
    """
    Generates synthetic data based on dynamically inferred column category.
    """
    inferred_category = infer_column_category(col_name, existing_data)

    if "name" in inferred_category:
        return fake.name()
    elif "organization" in inferred_category:
        return fake.company()
    elif "region" in inferred_category:
        return fake.country()
    elif "date" in inferred_category:
        return fake.date()
    elif "timestamp" in inferred_category:
        return fake.date_time()
    elif "unit" in inferred_category:
        return round(random.uniform(1.0, 500.0), 2)
    elif "currency" in inferred_category:
        return round(random.uniform(10.0, 10000.0), 2)
    elif "boolean" in inferred_category:
        return random.choice(["Y", "N"])
    else:
        return fake.word()

def generate_table_data(schema, num_rows=1000):
    """
    Generates synthetic data dynamically for an entire schema.
    """
    data = []
    existing_categories = set(schema.keys())  # Track existing column categories

    for _ in range(num_rows):
        row_data = {col: generate_dynamic_value(col, existing_categories) for col in schema}
        data.append(Row(**row_data))

    return spark.createDataFrame(data)

# Example Schema
schema = {
    "Classification": "string",
    "County": "string",
    "subtype": "string",
    "Organisation": "string",
    "Unit": "decimal",
    "USD Value": "decimal",
    "ingestion_date": "date",
    "Ingestion_timestamp": "timestamp",
    "extraction_filed": "boolean",
    "Name": "string"
}

# Generate Data
df = generate_table_data(schema, num_rows=1000)
df.show(truncate=False)

######################

import spacy
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import umap
from fuzzywuzzy import process
from faker import Faker
import random
from pyspark.sql import SparkSession, Row

# Initialize Spark session
spark = SparkSession.builder.appName("DynamicSyntheticDataGenerator").getOrCreate()

# Load NLP model
nlp = spacy.load("en_core_web_sm")
fake = Faker()

# ========================== STEP 1: DYNAMICALLY EXTRACT SCHEMA METADATA ========================== #
def get_schema_metadata(table_name):
    """
    Dynamically extracts schema metadata from a database or an existing DataFrame.
    In a real-world scenario, replace this with actual schema extraction from a database.
    """
    df = spark.read.table(table_name)  # Replace with actual DB read operation
    schema_metadata = {col_name: dtype for col_name, dtype in df.dtypes}  # Extract column names and types
    return schema_metadata

# ========================== STEP 2: CLASSIFY COLUMN VALUES DYNAMICALLY ========================== #
def classify_column_values(col_name, existing_data=None):
    """
    Dynamically classifies a column based on NLP, embeddings, and fuzzy matching.
    """
    col_name_cleaned = col_name.lower().replace("_", " ")

    # Step 1: Named Entity Recognition (NER)
    doc = nlp(col_name_cleaned)
    for ent in doc.ents:
        if ent.label_ in ["PERSON"]:
            return "name"
        elif ent.label_ in ["ORG"]:
            return "organization"
        elif ent.label_ in ["GPE", "LOC"]:
            return "region"
        elif ent.label_ in ["DATE", "TIME"]:
            return "date" if "date" in col_name_cleaned else "timestamp"

    # Step 2: Clustering-based Classification (for unknown columns)
    vector = np.array(doc.vector).reshape(1, -1)
    umap_model = umap.UMAP(n_components=2, random_state=42)
    reduced_vector = umap_model.fit_transform(vector)

    kmeans = KMeans(n_clusters=5, random_state=42)
    cluster = kmeans.fit_predict(reduced_vector)

    # Step 3: Fuzzy Matching on Existing Data
    if existing_data is not None:
        best_match, score = process.extractOne(col_name_cleaned, existing_data)
        if score > 80:
            return best_match  # Assign to an existing known category

    return f"category_{cluster[0]}"  # Assign to a dynamically inferred category

# ========================== STEP 3: GENERATE SYNTHETIC DATA BASED ON COLUMN TYPE ========================== #
def generate_synthetic_value(col_name, existing_data=None):
    """
    Generates synthetic data based on dynamically inferred column type.
    """
    inferred_category = classify_column_values(col_name, existing_data)

    if "name" in inferred_category:
        return fake.name()
    elif "organization" in inferred_category:
        return fake.company()
    elif "region" in inferred_category:
        return fake.country()
    elif "date" in inferred_category:
        return fake.date()
    elif "timestamp" in inferred_category:
        return fake.date_time()
    elif "unit" in inferred_category:
        return round(random.uniform(1.0, 500.0), 2)
    elif "currency" in inferred_category:
        return round(random.uniform(10.0, 10000.0), 2)
    elif "boolean" in inferred_category:
        return random.choice(["Y", "N"])
    else:
        return fake.word()

# ========================== STEP 4: GENERATE SYNTHETIC DATA FOR A GIVEN TABLE ========================== #
def generate_table_data(table_name, num_rows=1000):
    """
    Generates synthetic data dynamically for an entire table using its schema.
    """
    schema = get_schema_metadata(table_name)
    existing_categories = set(schema.keys())  # Track existing column categories

    data = []
    for _ in range(num_rows):
        row_data = {col: generate_synthetic_value(col, existing_categories) for col in schema}
        data.append(Row(**row_data))

    return spark.createDataFrame(data)

# ========================== STEP 5: RUN SCRIPT ========================== #
if __name__ == "__main__":
    table_name = "your_table_name"  # Change to actual table name in your database
    df = generate_table_data(table_name, num_rows=1000)
    df.show(truncate=False)

#############################################################################################################

import spacy
import numpy as np
import pandas as pd
import random
from pyspark.sql import SparkSession, Row
from faker import Faker
from fuzzywuzzy import process
import re
import html
from datetime import datetime

# Initialize Spark session
spark = SparkSession.builder.appName("DynamicSyntheticDataGenerator").getOrCreate()

# Load NLP model and Faker
nlp = spacy.load("en_core_web_sm")
fake = Faker()
Faker.seed(42)  # Consistency across multiple runs

# ========================== STEP 1: DYNAMICALLY EXTRACT SCHEMA METADATA ========================== #
def get_schema_metadata(table_name):
    """
    Dynamically extracts schema metadata from a Hive/Delta table.
    """
    df = spark.read.table(table_name)  # Read from Hive/Delta
    schema_metadata = {col_name: dtype for col_name, dtype in df.dtypes}
    return schema_metadata

# ========================== STEP 2: CLASSIFY COLUMN VALUES DYNAMICALLY ========================== #
def classify_column_values(col_name, existing_data=None):
    """
    Dynamically classifies a column based on regex patterns and NLP.
    """
    col_name_cleaned = col_name.lower().replace("_", " ")

    # Pattern-based classification
    if re.match(r".*date.*", col_name_cleaned):
        return "date"
    elif re.match(r".*time.*", col_name_cleaned):
        return "timestamp"
    elif re.match(r".*comment.*|.*note.*|.*desc.*", col_name_cleaned):
        return "comment"
    elif re.match(r".*id.*|.*key.*|.*code.*", col_name_cleaned):
        return "identifier"
    elif re.match(r"^[A-Z]{2,}\d{3}.*", col_name):
        return "pattern_alphanumeric"
    elif re.match(r".*account.*|.*loan.*|.*depo.*", col_name_cleaned):
        return "financial_code"
    elif "name" in col_name_cleaned:
        return "name"
    elif "org" in col_name_cleaned or "company" in col_name_cleaned:
        return "organization"

    # NLP-based classification fallback
    doc = nlp(col_name_cleaned)
    for ent in doc.ents:
        if ent.label_ in ["PERSON"]:
            return "name"
        elif ent.label_ in ["ORG"]:
            return "organization"
        elif ent.label_ in ["GPE", "LOC"]:
            return "region"
        elif ent.label_ in ["DATE"]:
            return "date"

    # Default if no match
    return "unknown"

# ========================== STEP 3: GENERATE SYNTHETIC VALUE BASED ON CLASSIFICATION ========================== #
def generate_synthetic_value(col_name, existing_data=None):
    """
    Generates synthetic data based on column type with pattern retention.
    """
    inferred_category = classify_column_values(col_name, existing_data)

    # Generate values based on identified types
    if inferred_category == "name":
        return fake.name()
    elif inferred_category == "organization":
        return fake.company()
    elif inferred_category == "date":
        return fake.date()
    elif inferred_category == "timestamp":
        return fake.date_time()
    elif inferred_category == "comment":
        return html.escape(fake.sentence() + " " + fake.paragraph())
    elif inferred_category == "identifier":
        return fake.uuid4()
    elif inferred_category == "pattern_alphanumeric":
        prefix = col_name[:3].upper()
        suffix = str(random.randint(100, 999))
        return f"{prefix}_{suffix}"
    elif inferred_category == "financial_code":
        return f"{col_name[:4].upper()}_{random.randint(100, 999)}"
    elif inferred_category == "boolean":
        return random.choice(["Y", "N"])
    else:
        return fake.word()

# ========================== STEP 4: GENERATE SYNTHETIC DATA FOR A TABLE ========================== #
def generate_table_data(table_name, partition_column=None, partition_value=None, num_rows=1000):
    """
    Generates synthetic data dynamically for an entire table using its schema.
    Supports partitioning and retains uniqueness across runs.
    """
    schema = get_schema_metadata(table_name)
    existing_categories = set(schema.keys())

    data = []
    for _ in range(num_rows):
        row_data = {}

        for col, dtype in schema.items():
            # Preserve partitioning logic if applied
            if col == partition_column and partition_value:
                row_data[col] = partition_value
            else:
                row_data[col] = generate_synthetic_value(col, existing_categories)

        data.append(Row(**row_data))

    return spark.createDataFrame(data)

# ========================== STEP 5: RUN SCRIPT ========================== #
if __name__ == "__main__":
    table_name = "your_table_name"  # Change to actual table name in Hive/Delta
    partition_column = "ingestion_date"  # Optional partition column
    partition_value = "2023-04-05"  # Optional partition value

    # Generate data for partition or full table
    df = generate_table_data(table_name, partition_column, partition_value, num_rows=1000)
    df.show(truncate=False)

