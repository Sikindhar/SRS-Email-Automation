from pymongo import MongoClient
import yaml

def test_connection():
    try:
        with open('config/config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        
        client = MongoClient(config['database']['connection_string'])
        db = client[config['database']['database_name']]
        client.server_info()
        print("Successfully connected to MongoDB!")
        return True
    except Exception as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()