import os
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from model import PhishingDetector
import argparse
import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

def load_data(data_dir):
    """
    Load the dataset from CSV files
    """
    train_df = pd.read_csv(os.path.join(data_dir, 'train_urls.csv'))
    val_df = pd.read_csv(os.path.join(data_dir, 'val_urls.csv'))
    test_df = pd.read_csv(os.path.join(data_dir, 'test_urls.csv'))
    
    print(f"Train set size: {len(train_df)}")
    print(f"Validation set size: {len(val_df)}")
    print(f"Test set size: {len(test_df)}")
    
    # Check class distribution
    print("\nClass distribution:")
    print(f"Train - Phishing: {train_df['label'].sum()} ({train_df['label'].mean()*100:.2f}%), Legitimate: {len(train_df) - train_df['label'].sum()}")
    print(f"Val - Phishing: {val_df['label'].sum()} ({val_df['label'].mean()*100:.2f}%), Legitimate: {len(val_df) - val_df['label'].sum()}")
    print(f"Test - Phishing: {test_df['label'].sum()} ({test_df['label'].mean()*100:.2f}%), Legitimate: {len(test_df) - test_df['label'].sum()}")
    
    return train_df, val_df, test_df

def train_and_evaluate_models(data_dir, model_dir, epochs=5):
    """
    Train both CNN and TF-IDF models
    """
    # Load data
    train_df, val_df, test_df = load_data(data_dir)
    
    # Initialize detector
    detector = PhishingDetector()
    
    # Create directories
    os.makedirs(model_dir, exist_ok=True)
    
    # Train CNN model
    print("\nTraining CNN model...")
    cnn_model = detector.build_cnn_model()
    
    # Preprocess data
    train_cnn = detector.preprocess_cnn_data(train_df['url'].tolist(), fit=True)
    val_cnn = detector.preprocess_cnn_data(val_df['url'].tolist())
    
    # Convert labels
    train_labels = train_df['label'].values
    val_labels = val_df['label'].values
    
    # Callbacks - Fix the filepath to include .keras extension
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True),
        ModelCheckpoint(
            filepath=os.path.join(model_dir, 'cnn_checkpoint.keras'),
            monitor='val_accuracy',
            save_best_only=True
        )
    ]
    
    # Train model
    cnn_history = cnn_model.fit(
        train_cnn,
        train_labels,
        validation_data=(val_cnn, val_labels),
        epochs=epochs,
        batch_size=32,
        callbacks=callbacks,
        verbose=1
    )
    
    # Train TF-IDF model
    print("\nTraining TF-IDF model...")
    tfidf_model = detector.build_tfidf_model()
    
    # Preprocess data
    train_tfidf = detector.preprocess_tfidf_data(train_df['url'].tolist(), fit=True)
    val_tfidf = detector.preprocess_tfidf_data(val_df['url'].tolist())
    
    # Callbacks - Fix the filepath to include .keras extension
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True),
        ModelCheckpoint(
            filepath=os.path.join(model_dir, 'tfidf_checkpoint.keras'),
            monitor='val_accuracy',
            save_best_only=True
        )
    ]
    
    # Train model
    tfidf_history = tfidf_model.fit(
        train_tfidf,
        train_labels,
        validation_data=(val_tfidf, val_labels),
        epochs=epochs,
        batch_size=32,
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate models
    print("\nEvaluating models on test set...")
    test_cnn = detector.preprocess_cnn_data(test_df['url'].tolist())
    test_tfidf = detector.preprocess_tfidf_data(test_df['url'].tolist())
    test_labels = test_df['label'].values
    
    # CNN predictions
    cnn_raw_preds = cnn_model.predict(test_cnn)
    cnn_preds = (cnn_raw_preds > 0.5).astype(int).flatten()
    
    # TF-IDF predictions
    tfidf_raw_preds = tfidf_model.predict(test_tfidf)
    tfidf_preds = (tfidf_raw_preds > 0.5).astype(int).flatten()
    
    # Print metrics
    print("\nCNN Model Metrics:")
    print(f"Accuracy: {accuracy_score(test_labels, cnn_preds):.4f}")
    print(f"Precision: {precision_score(test_labels, cnn_preds):.4f}")
    print(f"Recall: {recall_score(test_labels, cnn_preds):.4f}")
    print(f"F1 Score: {f1_score(test_labels, cnn_preds):.4f}")
    print("\nDetailed Classification Report:")
    print(classification_report(test_labels, cnn_preds))
    
    print("\nTF-IDF Model Metrics:")
    print(f"Accuracy: {accuracy_score(test_labels, tfidf_preds):.4f}")
    print(f"Precision: {precision_score(test_labels, tfidf_preds):.4f}")
    print(f"Recall: {recall_score(test_labels, tfidf_preds):.4f}")
    print(f"F1 Score: {f1_score(test_labels, tfidf_preds):.4f}")
    print("\nDetailed Classification Report:")
    print(classification_report(test_labels, tfidf_preds))
    
    # Plot training history
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(cnn_history.history['accuracy'])
    plt.plot(cnn_history.history['val_accuracy'])
    plt.title('CNN Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    
    plt.subplot(2, 2, 2)
    plt.plot(cnn_history.history['loss'])
    plt.plot(cnn_history.history['val_loss'])
    plt.title('CNN Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper right')
    
    plt.subplot(2, 2, 3)
    plt.plot(tfidf_history.history['accuracy'])
    plt.plot(tfidf_history.history['val_accuracy'])
    plt.title('TF-IDF Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    
    plt.subplot(2, 2, 4)
    plt.plot(tfidf_history.history['loss'])
    plt.plot(tfidf_history.history['val_loss'])
    plt.title('TF-IDF Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(model_dir, 'training_history.png'))
    
    # Test some sample URLs
    print("\nTesting sample phishing and legitimate URLs:")
    test_urls = [
        "http://paypal.com-secure-login.net/login.html",  # Phishing
        "https://support-appleld.com.secureupdate.duilawyeryork.com/ap/",  # Phishing
        "http://rgipt.ac.in",  # Legitimate
        "http://www.iracing.com/tracks/gateway-motorsports-park/",  # Legitimate
        "http://appleid.apple.com-app.es/",  # Phishing
        "http://www.mutuo.it"  # Legitimate
    ]
    
    expected_labels = [1, 1, 0, 0, 1, 0]
    
    # Get predictions from each model
    cnn_samples = detector.preprocess_cnn_data(test_urls)
    cnn_sample_preds = (cnn_model.predict(cnn_samples) > 0.5).astype(int).flatten()
    
    tfidf_samples = detector.preprocess_tfidf_data(test_urls)
    tfidf_sample_preds = (tfidf_model.predict(tfidf_samples) > 0.5).astype(int).flatten()
    
    # Print results
    print("\nSample URL test results:")
    print("URL | Expected | CNN | TF-IDF")
    print("-" * 50)
    for i, url in enumerate(test_urls):
        print(f"{url[:30]}... | {expected_labels[i]} | {cnn_sample_preds[i]} | {tfidf_sample_preds[i]}")
    
    # Save models
    detector.save(model_dir)
    print(f"\nModels saved to {model_dir}")
    
    return detector

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train phishing detection models')
    parser.add_argument('--data_dir', type=str, default='../data/processed',
                        help='Directory containing processed datasets')
    parser.add_argument('--model_dir', type=str, default='../models/cnn_phishing',
                        help='Directory to save trained models')
    parser.add_argument('--epochs', type=int, default=10,
                        help='Number of training epochs')
    
    args = parser.parse_args()
    
    # Fix for TensorFlow memory issues
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(e)
    
    # Train models
    detector = train_and_evaluate_models(args.data_dir, args.model_dir, args.epochs)