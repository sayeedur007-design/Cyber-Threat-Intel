import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

class ThreatClassifier:
    def __init__(self):
        # A curated representative dataset for CTI classification
        # Categories: phishing, malware, ransomware, benign
        self.data = [
            # Phishing
            ("Urgent: Your account password expires in 2 hours. Click here to reset now.", "phishing"),
            ("Your parcel is waiting at the post office. Please verify your address at this link.", "phishing"),
            ("Microsoft Security Alert: Unusual login detected from Russia. Verify your identity.", "phishing"),
            ("Payroll update: Your monthly payslip is ready for download in PDF format.", "phishing"),
            ("Action Required: Your subscription has been suspended due to payment failure.", "phishing"),
            
            # Malware
            ("The attachment contains a macro-enabled Excel sheet for checking invoice details.", "malware"),
            ("Executing powershell -enc BASE64_STRING to download payload from remote server.", "malware"),
            ("Suspicious process detected connecting to known C2 server at 185.12.33.4.", "malware"),
            ("Malicious DLL injection attempt detected in explorer.exe process memory.", "malware"),
            ("Trojan dropper identified in system temp directory attempting to persistence.", "malware"),
            
            # Ransomware
            ("Your files have been encrypted using AES-256 and RSA-2048 encryption algorithms.", "ransomware"),
            ("All your sensitive data has been leaked to our private tor site. Pay 2 BTC now.", "ransomware"),
            ("WannaCry infection detected. System files locked. Please contact the help desk.", "ransomware"),
            ("Critical: REvil ransomware variant detected attempting to delete shadow copies.", "ransomware"),
            ("Do NOT restart your computer or your decryption key will be permanently deleted.", "ransomware"),
            
            # Benign / Normal
            ("User logged in successfully via VPN from authorized corporate gateway.", "benign"),
            ("Standard Windows Update KB5034441 initiated on workstation-04 at 03:00 AM.", "benign"),
            ("Backup completed successfully for the finance database on central storage server.", "benign"),
            ("Network traffic within normal baselines for the production subnet 10.0.5.0/24.", "benign"),
            ("Employee accessed the internal HR portal for annual leave request submission.", "benign")
        ]
        
        # Build the pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), stop_words='english')),
            ('nb', MultinomialNB(alpha=0.1))
        ])
        
        self._train()

    def _train(self):
        """Train the classifier on the curated dataset."""
        df = pd.DataFrame(self.data, columns=['text', 'label'])
        self.pipeline.fit(df['text'], df['label'])

    def predict(self, text: str):
        """Predict the category and return probabilities."""
        if not text.strip():
            return "unknown", 0.0
            
        prediction = self.pipeline.predict([text])[0]
        # Get probability for the predicted class
        probs = self.pipeline.predict_proba([text])[0]
        # Map classes to their indices
        class_idx = list(self.pipeline.classes_).index(prediction)
        confidence = probs[class_idx]
        
        return prediction, confidence

    def get_all_probs(self, text: str):
        """Return a dictionary of all category probabilities."""
        if not text.strip():
            return {}
        
        probs = self.pipeline.predict_proba([text])[0]
        classes = self.pipeline.classes_
        return dict(zip(classes, probs))
