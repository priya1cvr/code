pip install sklearn umap-learn numpy faker

import spacy
import numpy as np
from sklearn.cluster import KMeans
import umap

nlp = spacy.load("en_core_web_sm")

# Predefined categories for mapping column names
COLUMN_CATEGORIES = [
    "name", "email", "phone", "address", "company", "city", "country", "amount", "price",
    "date", "timestamp", "category", "product", "review", "description", "alphanumeric"
]

def infer_column_meaning(col_name):
    """
    Uses NLP embeddings + clustering to dynamically classify column names.
    """
    col_name_cleaned = col_name.lower().replace("_", " ")
    doc = nlp(col_name_cleaned)
   
    # Convert column name to vector
    vector = np.array(doc.vector).reshape(1, -1)

    # Reduce dimensionality using UMAP
    umap_model = umap.UMAP(n_components=2, random_state=42)
    reduced_vector = umap_model.fit_transform(vector)

    # Cluster classification using K-Means
    kmeans = KMeans(n_clusters=len(COLUMN_CATEGORIES), random_state=42)
    cluster = kmeans.fit_predict(reduced_vector)

    return COLUMN_CATEGORIES[cluster[0]]  # Return classified category



from faker import Faker
import random
import datetime
import string

fake = Faker()

def generate_synthetic_value(col_name, col_type, row_index=0):
    """
    Generates synthetic data based on dynamically inferred column type.
    """
    meaning = infer_column_meaning(col_name)

    if meaning == "name":
        return fake.name()
    elif meaning == "email":
        return fake.email()
    elif meaning == "phone":
        return fake.phone_number()
    elif meaning == "address":
        return fake.address()
    elif meaning == "company":
        return fake.company()
    elif meaning == "city":
        return fake.city()
    elif meaning == "country":
        return fake.country()
    elif meaning == "amount" or meaning == "price":
        return round(random.uniform(1.0, 10000.0), 2)
    elif meaning == "category" or meaning == "product":
        return fake.word()
    elif meaning == "review" or meaning == "description":
        return fake.sentence(nb_words=12)
    elif meaning == "alphanumeric":
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    elif meaning == "date":
        return generate_time_series(row_index)
    elif "int" in col_type or "bigint" in col_type:
        return random.randint(1, 10000)
    elif "decimal" in col_type:
        return round(random.uniform(1.0, 1000.0), 2)
    else:
        return fake.sentence(nb_words=5)  # Default fallback


def generate_time_series(index, start_date="2020-01-01"):
    """
    Generates sequential time-series data for date columns.
    """
    base_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    delta = datetime.timedelta(days=index)
    return (base_date + delta).strftime("%Y-%m-%d")


from pyspark.sql import Row

def generate_table_data(table_name, columns, num_rows=1000):
    """
    Generates synthetic data for a table using NLP and pattern-based generation.
    """
    data = []

    for row_index in range(num_rows):
        row_data = {col[0]: generate_synthetic_value(col[0], col[1], row_index) for col in columns}
        data.append(Row(**row_data))

    df = spark.createDataFrame(data)
    return df

def generate_schema_data(schema_name, num_rows=1000):
    """
    Generates synthetic data for all tables in a schema dynamically.
    """
    schema_metadata = get_schema_metadata(schema_name)
    dataframes = {}

    for table, columns in schema_metadata.items():
        print(f"Generating data for table: {table}")
        df = generate_table_data(table, columns, num_rows)
        dataframes[table] = df

    for table, df in dataframes.items():
        df.write.mode("overwrite").format("parquet").save(f"dbfs:/synthetic_data/{schema_name}/{table}")

generate_schema_data("your_schema_name", num_rows=5000)
