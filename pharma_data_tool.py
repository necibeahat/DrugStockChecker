#!/usr/bin/env python3
"""
Custom Strands tool for pharmaceutical data analysis.

This tool integrates with your existing data processing pipeline
to provide AI agents access to pharmaceutical news and shortage data.
"""

import json
import os
from typing import List, Dict, Any
from strands import tool

@tool
def search_pharma_news(query: str, limit: int = 5) -> str:
    """Search pharmaceutical news data for relevant articles.
    
    Args:
        query: Search term or topic (e.g., "ALS", "drug shortage", "regulatory")
        limit: Maximum number of results to return (default: 5)
    
    Returns:
        Formatted string with relevant news articles and details
    """
    try:
        # Load the main news data file
        news_file = "data/Navlin News/als_news_all.json"
        if not os.path.exists(news_file):
            return f"❌ News data file not found: {news_file}"
        
        with open(news_file, 'r', encoding='utf-8-sig') as f:
            news_data = json.load(f)
        
        # Simple text search in news content
        query_lower = query.lower()
        matching_articles = []
        
        # Handle different data structures
        articles = news_data if isinstance(news_data, list) else news_data.get('articles', [])
        
        for article in articles:
            # Search in title, content, and keywords
            searchable_text = ""
            if 'title' in article:
                searchable_text += article['title'].lower() + " "
            if 'content' in article:
                searchable_text += str(article.get('content', '')).lower() + " "
            if 'keywords' in article:
                searchable_text += " ".join(article.get('keywords', [])).lower()
            
            if query_lower in searchable_text:
                matching_articles.append(article)
                if len(matching_articles) >= limit:
                    break
        
        if not matching_articles:
            return f"No articles found matching '{query}'"
        
        # Format results
        result = f"Found {len(matching_articles)} articles matching '{query}':\n\n"
        for i, article in enumerate(matching_articles, 1):
            result += f"{i}. {article.get('title', 'No title')}\n"
            if 'date' in article:
                result += f"   Date: {article['date']}\n"
            if 'content' in article:
                content = str(article['content'])[:200] + "..." if len(str(article['content'])) > 200 else str(article['content'])
                result += f"   Summary: {content}\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error searching news data: {str(e)}"

@tool
def get_drug_shortage_info(product_name: str = None) -> str:
    """Get information about drug shortages.
    
    Args:
        product_name: Specific product to search for (optional)
    
    Returns:
        Information about drug shortages, filtered by product if specified
    """
    try:
        # Find the most recent shortage data file
        shortage_files = [f for f in os.listdir('data') if f.startswith('drug_shortage_combined_')]
        if not shortage_files:
            return "❌ No drug shortage data files found"
        
        # Use the most recent file
        latest_file = sorted(shortage_files)[-1]
        shortage_file = f"data/{latest_file}"
        
        with open(shortage_file, 'r') as f:
            shortage_data = json.load(f)
        
        # Handle different data structures
        shortages = shortage_data if isinstance(shortage_data, list) else shortage_data.get('shortages', [])
        
        if product_name:
            # Filter by product name
            product_lower = product_name.lower()
            matching_shortages = [
                shortage for shortage in shortages
                if product_lower in str(shortage.get('product_name', '')).lower() or
                   product_lower in str(shortage.get('ingredient', '')).lower()
            ]
            
            if not matching_shortages:
                return f"No shortages found for product '{product_name}'"
            
            result = f"Found {len(matching_shortages)} shortage(s) for '{product_name}':\n\n"
            shortages = matching_shortages
        else:
            result = f"Current drug shortage summary ({len(shortages)} total shortages):\n\n"
            # Limit to first 10 for overview
            shortages = shortages[:10]
        
        for i, shortage in enumerate(shortages, 1):
            result += f"{i}. {shortage.get('product_name', 'Unknown product')}\n"
            if 'ingredient' in shortage:
                result += f"   Active ingredient: {shortage['ingredient']}\n"
            if 'date_reported' in shortage:
                result += f"   Reported: {shortage['date_reported']}\n"
            if 'countries' in shortage:
                result += f"   Affected countries: {', '.join(shortage['countries'])}\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error accessing shortage data: {str(e)}"

@tool
def analyze_pharma_trends(timeframe: str = "recent") -> str:
    """Analyze trends in pharmaceutical news and shortages.
    
    Args:
        timeframe: Time period to analyze ("recent", "monthly", "all")
    
    Returns:
        Analysis of trends and patterns in the data
    """
    try:
        analysis = f"📊 Pharmaceutical Trends Analysis ({timeframe}):\n\n"
        
        # Analyze news data
        news_file = "data/Navlin News/als_news_all.json"
        if os.path.exists(news_file):
            with open(news_file, 'r', encoding='utf-8-sig') as f:
                news_data = json.load(f)
            
            articles = news_data if isinstance(news_data, list) else news_data.get('articles', [])
            analysis += f"📰 News Analysis:\n"
            analysis += f"   - Total articles: {len(articles)}\n"
            
            # Count by keywords if available
            keyword_counts = {}
            for article in articles:
                keywords = article.get('keywords', [])
                for keyword in keywords:
                    keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            if keyword_counts:
                top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                analysis += f"   - Top topics: {', '.join([f'{k} ({v})' for k, v in top_keywords])}\n"
        
        # Analyze shortage data
        shortage_files = [f for f in os.listdir('data') if f.startswith('drug_shortage_combined_')]
        if shortage_files:
            latest_file = sorted(shortage_files)[-1]
            with open(f"data/{latest_file}", 'r') as f:
                shortage_data = json.load(f)
            
            shortages = shortage_data if isinstance(shortage_data, list) else shortage_data.get('shortages', [])
            analysis += f"\n💊 Shortage Analysis:\n"
            analysis += f"   - Total shortages: {len(shortages)}\n"
            
            # Count by country
            country_counts = {}
            for shortage in shortages:
                countries = shortage.get('countries', [])
                for country in countries:
                    country_counts[country] = country_counts.get(country, 0) + 1
            
            if country_counts:
                top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                analysis += f"   - Most affected regions: {', '.join([f'{k} ({v})' for k, v in top_countries])}\n"
        
        analysis += "\n💡 Key insights available through detailed queries using search_pharma_news() and get_drug_shortage_info()"
        
        return analysis
        
    except Exception as e:
        return f"❌ Error analyzing trends: {str(e)}"

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing pharmaceutical data tools...")
    
    # Test news search
    print("\n1. Testing news search:")
    result = search_pharma_news("ALS", 3)
    print(result)
    
    # Test shortage info
    print("\n2. Testing shortage info:")
    result = get_drug_shortage_info()
    print(result)
    
    # Test trend analysis
    print("\n3. Testing trend analysis:")
    result = analyze_pharma_trends()
    print(result)