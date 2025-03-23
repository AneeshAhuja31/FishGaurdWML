import os
import numpy as np
from model import PhishingDetector
import argparse

def test_model(model_dir):
    """
    Test the phishing detection model
    """
    # Load the detector
    detector = PhishingDetector(model_dir)
    
    # Some test URLs
    test_urls = [
        "http://src.0.8.5.4/?uu&",  # Legitimate
        "http://paypal.com-secure-login.net/login.html",  # Phishing
        "https://www.goggle.com",  # Legitimate
        "https://www.huschhus.ch/sitebar/index.php",  # Legitimate
        "http://www.cel.com/pdf/misc/zic13_pktanlz_sm.pdf",  # Legitimate
        "http://eltronesia.id/.well-known/pki-validation/raiffeisen/lograiffeisenFull/sms.php"  # Legitimate
    ]
    
    # Get predictions
    predictions = detector.predict(test_urls)
    
    # Print results
    print("\nTest URL Results:")
    for i, url in enumerate(test_urls):
        result = "Phishing" if predictions[i] == 1 else "Legitimate"
        print(f"{url}: {result}")
    
    return predictions

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test phishing detection model')
    parser.add_argument('--model_dir', type=str, default='../models/cnn_phishing',
                        help='Directory containing trained models')
    
    args = parser.parse_args()
    
    # Test the model
    predictions = test_model(args.model_dir)