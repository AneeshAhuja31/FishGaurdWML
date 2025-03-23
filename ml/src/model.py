import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout, Input, Conv1D, GlobalMaxPooling1D, Embedding
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle
import os
import joblib
import re

class PhishingDetector:
    def __init__(self, model_path=None):
        self.cnn_model = None
        self.tfidf_model = None
        self.tokenizer = None
        self.tfidf_vectorizer = None
        self.max_length = 100  # Max URL length to consider
        self.max_words = 10000  # Vocabulary size
        
        if model_path:
            self.load(model_path)
        
    def build_cnn_model(self):
        """
        Build a CNN-based model for URL classification
        """
        # Input layer
        input_layer = Input(shape=(self.max_length,))
        
        # Embedding layer - removed deprecated input_length parameter
        embedding_layer = Embedding(
            input_dim=self.max_words + 1,
            output_dim=64
        )(input_layer)
        
        # CNN layers
        conv1 = Conv1D(filters=64, kernel_size=3, activation='relu')(embedding_layer)
        pool1 = GlobalMaxPooling1D()(conv1)
        
        # Dense layers
        dense1 = Dense(64, activation='relu')(pool1)
        dropout1 = Dropout(0.2)(dense1)
        output = Dense(1, activation='sigmoid')(dropout1)
        
        # Create model
        self.cnn_model = Model(inputs=input_layer, outputs=output)
        
        # Compile model
        self.cnn_model.compile(
            optimizer=Adam(learning_rate=1e-3),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return self.cnn_model
    
    def build_tfidf_model(self):
        """
        Build a TF-IDF based model as fallback
        """
        # Initialize vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            analyzer='char', 
            ngram_range=(3, 5),
            max_features=5000,
            lowercase=True
        )
        
        # Define a simple model
        input_layer = Input(shape=(5000,))
        x = Dense(128, activation='relu')(input_layer)
        x = Dropout(0.25)(x)
        x = Dense(64, activation='relu')(x)
        x = Dropout(0.2)(x)
        output = Dense(1, activation='sigmoid')(x)
        
        # Create model
        self.tfidf_model = Model(inputs=input_layer, outputs=output)
        
        # Compile model
        self.tfidf_model.compile(
            optimizer=Adam(learning_rate=1e-3),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return self.tfidf_model
    
    def preprocess_urls(self, urls):
        """
        Preprocess URLs for both models
        """
        # URL cleaning function
        def clean_url(url):
            # Convert to lowercase
            url = url.lower()
            # Remove http/https/www prefixes
            url = re.sub(r'^https?://(www\.)?', '', url)
            # Remove trailing slashes
            url = re.sub(r'/$', '', url)
            return url
        
        # Apply cleaning to all URLs
        return [clean_url(url) for url in urls]
    
    def preprocess_cnn_data(self, urls, fit=False):
        """
        Convert URLs to CNN inputs
        """
        # Clean URLs
        cleaned_urls = self.preprocess_urls(urls)
        
        # Create or use tokenizer
        if fit or self.tokenizer is None:
            self.tokenizer = Tokenizer(num_words=self.max_words, char_level=True)
            self.tokenizer.fit_on_texts(cleaned_urls)
        
        # Convert to sequences
        sequences = self.tokenizer.texts_to_sequences(cleaned_urls)
        padded_sequences = pad_sequences(sequences, maxlen=self.max_length)
        
        return padded_sequences
    
    def preprocess_tfidf_data(self, urls, fit=False):
        """
        Convert URLs to TF-IDF features
        """
        # Clean URLs
        cleaned_urls = self.preprocess_urls(urls)
        
        # Create or transform with vectorizer
        if fit or self.tfidf_vectorizer is None:
            return self.tfidf_vectorizer.fit_transform(cleaned_urls).toarray()
        return self.tfidf_vectorizer.transform(cleaned_urls).toarray()
    
    def save(self, model_dir):
        """
        Save both models and preprocessing components
        """
        os.makedirs(model_dir, exist_ok=True)
        
        # Save CNN model - updated to use .keras extension
        if self.cnn_model:
            cnn_save_path = os.path.join(model_dir, 'cnn_model.keras')
            self.cnn_model.save(cnn_save_path)
            print(f"CNN model saved to {cnn_save_path}")
            
            tokenizer_path = os.path.join(model_dir, 'tokenizer.pickle')
            with open(tokenizer_path, 'wb') as handle:
                pickle.dump(self.tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
            print(f"Tokenizer saved to {tokenizer_path}")
            
        # Save TF-IDF model - updated to use .keras extension
        if self.tfidf_model:
            tfidf_save_path = os.path.join(model_dir, 'tfidf_model.keras')
            self.tfidf_model.save(tfidf_save_path)
            print(f"TF-IDF model saved to {tfidf_save_path}")
            
            vectorizer_path = os.path.join(model_dir, 'tfidf_vectorizer.pkl')
            joblib.dump(self.tfidf_vectorizer, vectorizer_path)
            print(f"TF-IDF vectorizer saved to {vectorizer_path}")
    
    def load(self, model_dir):
        """
        Load models and preprocessing components
        """
        # Load CNN model - updated to use .keras extension
        cnn_model_path = os.path.join(model_dir, 'cnn_model.keras')
        tokenizer_path = os.path.join(model_dir, 'tokenizer.pickle')
        
        if os.path.exists(cnn_model_path) and os.path.exists(tokenizer_path):
            self.cnn_model = load_model(cnn_model_path)
            with open(tokenizer_path, 'rb') as handle:
                self.tokenizer = pickle.load(handle)
            print("CNN model and tokenizer loaded successfully")
        else:
            print(f"Could not find CNN model at {cnn_model_path}")
        
        # Load TF-IDF model - updated to use .keras extension
        tfidf_model_path = os.path.join(model_dir, 'tfidf_model.keras')
        vectorizer_path = os.path.join(model_dir, 'tfidf_vectorizer.pkl')
        
        if os.path.exists(tfidf_model_path) and os.path.exists(vectorizer_path):
            self.tfidf_model = load_model(tfidf_model_path)
            self.tfidf_vectorizer = joblib.load(vectorizer_path)
            print("TF-IDF model and vectorizer loaded successfully")
        else:
            print(f"Could not find TF-IDF model at {tfidf_model_path}")
    
    def predict(self, urls):
        """
        Make predictions using CNN model with TF-IDF fallback
        """
        # Ensure we have a list of URLs
        if isinstance(urls, str):
            urls = [urls]
            
        predictions = np.zeros(len(urls), dtype=int)
        
        # Try CNN model first
        if self.cnn_model and self.tokenizer:
            try:
                print("Predicting with CNN model...")
                cnn_inputs = self.preprocess_cnn_data(urls)
                cnn_raw_predictions = self.cnn_model.predict(cnn_inputs)
                predictions = (cnn_raw_predictions > 0.5).astype(int).flatten()
                print(f"CNN raw predictions: {cnn_raw_predictions.flatten()}")
                
                # If all predictions are 0, try TF-IDF model
                if np.sum(predictions) == 0:
                    print("All CNN predictions are 0, trying TF-IDF model...")
                    raise Exception("Fallback to TF-IDF")
                    
                return predictions
            except Exception as e:
                print(f"CNN model error or fallback: {e}")
        else:
            print("No CNN model available")
        
        # Fallback to TF-IDF model
        if self.tfidf_model and self.tfidf_vectorizer:
            try:
                print("Predicting with TF-IDF model...")
                tfidf_features = self.preprocess_tfidf_data(urls)
                tfidf_raw_predictions = self.tfidf_model.predict(tfidf_features)
                predictions = (tfidf_raw_predictions > 0.5).astype(int).flatten()
                print(f"TF-IDF raw predictions: {tfidf_raw_predictions.flatten()}")
                return predictions
            except Exception as e:
                print(f"TF-IDF model error: {e}")
        else:
            print("No TF-IDF model available")
        
        # If all else fails, perform basic heuristic check
        print("Using heuristic fallback...")
        for i, url in enumerate(urls):
            # Basic heuristic for phishing detection
            url_lower = url.lower()
            suspicious_patterns = [
                'login', 'signin', 'verify', 'secure', 'account', 'password',
                'confirm', 'update', 'apple', 'paypal', 'bank', 'support'
            ]
            suspicious_domains = [
                '.com-', '-secure-', '.secureupdate.', '-app.', '.app.',
                'authenticate', 'verification', 'validate'
            ]
            
            # Check for phishing indicators
            score = 0
            for pattern in suspicious_patterns:
                if pattern in url_lower:
                    score += 1
            
            for domain in suspicious_domains:
                if domain in url_lower:
                    score += 2
            
            # Check for excessive subdomains or path segments
            dots = url.count('.')
            slashes = url.count('/')
            if dots > 3 or slashes > 4:
                score += 1
            
            # Final decision
            predictions[i] = 1 if score >= 3 else 0
            
        return predictions