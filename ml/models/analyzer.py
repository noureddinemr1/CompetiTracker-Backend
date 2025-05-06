import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import timedelta

# For numerical analysis and forecasting
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import lightgbm as lgb
import xgboost as xgb


# For text analysis
import spacy
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

# For recommendation engine
from sklearn.metrics.pairwise import cosine_similarity

class CompetitiveAnalysisAI:
    from pymongo import MongoClient
from bson.objectid import ObjectId

class CompetitiveAnalysisAI:
    def __init__(self, mongo_uri=None, db_name="CompetiTracker"):
        """
        Initialize with MongoDB connection
        
        Args:
            mongo_uri: MongoDB Atlas connection string
                      If None, will try to get from environment variable MONGODB_URI
            db_name: Name of your database in Atlas
        """
        # Get connection string from environment if not provided
        if mongo_uri is None:
            mongo_uri = os.getenv("MONGODB_ATLAS_URI")
            
            if mongo_uri is None:
                raise ValueError(
                    "Either provide mongo_uri or set MONGODB_ATLAS_URI environment variable"
                )
        
        # Initialize MongoDB connection with timeout settings
        self.client = MongoClient(
            mongo_uri,
            connectTimeoutMS=30000,  # 30 seconds
            socketTimeoutMS=30000,
            serverSelectionTimeoutMS=30000
        )
        
        # Verify connection works
        try:
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB Atlas!")
        except Exception as e:
            print("Failed to connect to MongoDB Atlas:", e)
            raise
        
        self.db = self.client[db_name]
        
        # Collections
        self.products_col = self.db['products']
        self.price_history_col = self.db['product_history']
        self.competitors_col = self.db['competitors']  
        
        # Initialize French NLP models
        self.nlp = spacy.load("fr_core_news_sm")
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        )
        
        # Initialize data cache
        self.product_data = None
        self.price_history = None
        
        # Model parameters
        self.price_change_threshold = 0.05
        self.stock_out_threshold = 3
        self.french_stopwords = set(nlp.Defaults.stop_words)
        
    def load_data(self, recent_days=30):
        """Load data from MongoDB Atlas"""
        # Load current product data
        product_data = list(self.products_col.find({}))
        self.product_data = pd.DataFrame(product_data)
        
        # Load price history (last 30 days by default)
        cutoff_date = datetime.now() - timedelta(days=recent_days)
        price_history = list(self.price_history_col.find({
            'date': {'$gte': cutoff_date}
        }))
        self.price_history = pd.DataFrame(price_history)
        
        # Basic data cleaning
        self._clean_data()

    def _clean_data(self):
        """Clean MongoDB data"""
        # Convert MongoDB ObjectId to string
        if '_id' in self.product_data.columns:
            self.product_data['_id'] = self.product_data['_id'].astype(str)
        
        if '_id' in self.price_history.columns:
            self.price_history['_id'] = self.price_history['_id'].astype(str)
        
        # Handle missing values
        self.product_data['description'].fillna('', inplace=True)
        
        # Convert dates if they're stored as strings
        if isinstance(self.price_history['date'].iloc[0], str):
            self.price_history['date'] = pd.to_datetime(self.price_history['date'])
        
        # Ensure numeric prices
        self.product_data['price'] = pd.to_numeric(self.product_data['price'], errors='coerce')
        self.price_history['price'] = pd.to_numeric(self.price_history['price'], errors='coerce')
        
        # Extract brand from name if needed
        if 'brand' not in self.product_data.columns:
            self.product_data['brand'] = self.product_data['name'].str.split().str[0]
            
    def analyze_price_trends(self, product_id):
        """Analyze price trends for a specific product"""
        product_history = self.price_history[self.price_history['product_id'] == product_id]
        
        if len(product_history) < 10:
            return {"status": "insufficient_data", "message": "Not enough data points for analysis"}
            
        # Time series analysis with ARIMA
        try:
            model = ARIMA(product_history['price'], order=(5,1,0))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=7)  # 7-day forecast
        except:
            # Fall back to simple moving average if ARIMA fails
            forecast = product_history['price'].rolling(7).mean().iloc[-7:]
        
        # Detect significant price changes
        price_changes = product_history['price'].pct_change()
        significant_changes = price_changes[abs(price_changes) > self.price_change_threshold]
        
        # Prophet forecasting
        prophet_df = product_history[['date', 'price']].rename(columns={'date': 'ds', 'price': 'y'})
        prophet_model = Prophet()
        prophet_model.fit(prophet_df)
        future = prophet_model.make_future_dataframe(periods=7)
        prophet_forecast = prophet_model.predict(future)
        
        return {
            "current_price": product_history['price'].iloc[-1],
            "7_day_forecast": forecast.tolist(),
            "prophet_forecast": prophet_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(7).to_dict('records'),
            "significant_changes": significant_changes.to_dict(),
            "price_stats": {
                "mean": product_history['price'].mean(),
                "min": product_history['price'].min(),
                "max": product_history['price'].max(),
                "std": product_history['price'].std()
            }
        }
    
    def analyze_competition(self):
        """Analyze competitive landscape"""
        # Cluster products by price and features
        features = self.product_data[['price', 'availability']].copy()
        features['availability'] = features['availability'].apply(lambda x: 1 if x > 0 else 0)
        
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Determine optimal number of clusters
        wcss = []
        for i in range(1, 11):
            kmeans = KMeans(n_clusters=i, random_state=42)
            kmeans.fit(scaled_features)
            wcss.append(kmeans.inertia_)
        
        # Use elbow method to find optimal k
        optimal_k = 3  # Default, can be improved with elbow detection
        if len(wcss) > 3:
            diffs = [wcss[i] - wcss[i+1] for i in range(len(wcss)-1)]
            optimal_k = diffs.index(max(diffs)) + 1
        
        kmeans = KMeans(n_clusters=optimal_k, random_state=42)
        clusters = kmeans.fit_predict(scaled_features)
        self.product_data['cluster'] = clusters
        
        # Analyze cluster characteristics
        cluster_stats = self.product_data.groupby('cluster')['price'].describe()
        
        return {
            "cluster_stats": cluster_stats.to_dict(),
            "product_clusters": self.product_data[['product_id', 'name', 'cluster']].to_dict('records')
        }
    
    def analyze_product_descriptions(self):
        """Perform NLP analysis on French product descriptions"""
        # Sample descriptions to avoid processing everything
        sample_descriptions = self.product_data['description'].sample(min(50, len(self.product_data)))
        
        # Sentiment analysis in French
        sentiments = self.sentiment_analyzer(sample_descriptions.tolist())
        
        # Custom French TF-IDF with stopword removal
        tfidf = TfidfVectorizer(
            max_features=50,
            stop_words=list(self.french_stopwords),  # French stopwords
            ngram_range=(1, 2)  # Include single words and 2-word phrases
        )
        tfidf_matrix = tfidf.fit_transform(self.product_data['description'])
        keywords = tfidf.get_feature_names_out()
        
        # Named Entity Recognition in French
        sample_text = " ".join(self.product_data['description'].sample(5).tolist())
        doc = self.nlp(sample_text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        return {
            "average_sentiment": np.mean([int(s['label'].split()[0]) for s in sentiments]),  # Convert 1-5 star ratings to numeric
            "top_keywords": keywords.tolist(),
            "common_entities": entities,
            "sentiment_distribution": [s['label'] for s in sentiments]
        }
    
    def generate_recommendations(self, product_id):
        """Generate strategic recommendations for a product"""
        product_info = self.product_data[self.product_data['product_id'] == product_id].iloc[0]
        price_analysis = self.analyze_price_trends(product_id)
        competition = self.analyze_competition()
        
        recommendations = []
        
        # Price-based recommendations
        current_price = price_analysis['current_price']
        cluster_avg = competition['cluster_stats'][str(product_info['cluster'])]['mean']
        
        if current_price > cluster_avg * 1.1:
            recommendations.append({
                "type": "price",
                "action": "consider_price_reduction",
                "reason": f"Your price (${current_price:.2f}) is 10% above cluster average (${cluster_avg:.2f})",
                "confidence": 0.7
            })
        elif current_price < cluster_avg * 0.9:
            recommendations.append({
                "type": "price",
                "action": "consider_price_increase",
                "reason": f"Your price (${current_price:.2f}) is 10% below cluster average (${cluster_avg:.2f})",
                "confidence": 0.6
            })
        
        # Stock availability recommendations
        stock_history = self.price_history[self.price_history['product_id'] == product_id]['availability']
        if stock_history.mean() < 0.5:
            recommendations.append({
                "type": "inventory",
                "action": "increase_stock",
                "reason": "Product has been out of stock frequently",
                "confidence": 0.8
            })
        
        # Competitive positioning
        cluster_products = self.product_data[self.product_data['cluster'] == product_info['cluster']]
        if len(cluster_products) > 5 and product_info['price'] == cluster_products['price'].max():
            recommendations.append({
                "type": "positioning",
                "action": "differentiate_product",
                "reason": "Your product is the most expensive in its cluster",
                "confidence": 0.75
            })
        
        return {
            "product_id": product_id,
            "product_name": product_info['name'],
            "recommendations": recommendations,
            "analysis": {
                "price": price_analysis,
                "competition": competition
            }
        }
    
    def visualize_data(self, product_id):
        """Generate visualizations for a product"""
        product_history = self.price_history[self.price_history['product_id'] == product_id]
        
        # Price trend plot
        plt.figure(figsize=(12, 6))
        sns.lineplot(x='date', y='price', data=product_history)
        plt.title(f"Price Trend for Product {product_id}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        price_plot = plt.gcf()
        
        # Availability plot
        plt.figure(figsize=(12, 6))
        sns.barplot(x='date', y='availability', data=product_history)
        plt.title(f"Availability History for Product {product_id}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        availability_plot = plt.gcf()
        
        return {
            "price_trend": price_plot,
            "availability_history": availability_plot
        }

    #Product Helpers
    
    def get_product_by_id(self, product_id):
        """Get single product document"""
        return self.products_col.find_one({'_id': ObjectId(product_id)})

    def get_price_history(self, product_id, days=30):
        """Get price history for specific product"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return list(self.price_history_col.find({
            'product_id': product_id,
            'date': {'$gte': cutoff_date}
        }).sort('date', 1))  # Sort by date ascending

    def update_analysis_results(self, product_id, analysis):
        """Store analysis results back to MongoDB"""
        self.products_col.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {'last_analysis': analysis, 'analyzed_at': datetime.now()}}
        )

# Example usage
if __name__ == "__main__":
    # Initialize the analyzer
    analyzer = CompetitiveAnalysisAI()
    
    # Load sample data (replace with your actual data paths)
    analyzer.load_data("products.csv", "price_history.csv")
    
    # Analyze a specific product
    product_id = "12345"
    analysis = analyzer.analyze_price_trends(product_id)
    recommendations = analyzer.generate_recommendations(product_id)
    
    # Print results
    print("Price Analysis:")
    print(analysis)
    
    print("\nRecommendations:")
    print(recommendations)
    
    # Visualize data
    plots = analyzer.visualize_data(product_id)
    plots['price_trend'].savefig("price_trend.png")
    plots['availability_history'].savefig("availability.png")