import requests
from tqdm.notebook import tqdm
from bs4 import BeautifulSoup
from textblob import TextBlob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from matplotlib_inline import backend_inline
backend_inline.set_matplotlib_formats('svg') 


def extract_text_from_html(html_path):
    text = ""
    try:
        # Read the HTML file
        with open(html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
    except Exception as e:
        print(f"Error reading HTML: {e}")
    return text


def extract_text_from_html2(html_file):
    with open(html_file, "r", encoding="utf-8") as file:
        html_content = file.read()

    # 使用 BeautifulSoup 解析 HTML 内容
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 移除脚本和样式表
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()  # 去除所有脚本和样式

    # 提取所有纯文本
    text = soup.get_text(separator="\n", strip=True)

    # 过滤掉多余的空行和非结构化文本
    meaningful_text = "\n".join(line for line in text.split("\n") if len(line.strip()) > 0)
    return meaningful_text


climate_keywords = {
    "Extreme Weather Risk Index": ["flood", "hurricane", "drought", "extreme heat", "storm"],
    "Greenhouse Gas Emission Intensity Index": ["carbon emission", "greenhouse gas", "emission intensity", "carbon dioxide", "emission reduction target"],
    "Climate Adaptability and Resilience Index": ["climate resilience", "infrastructure upgrade", "emergency plan", "climate adaptation", "adaptation plan"],
    "Renewable Energy Investment and Transition Progress Index": ["renewable energy", "solar power", "wind power", "low-carbon technology", "energy transition"],
    "Policy and Legal Risk Index": ["carbon tax", "emission trading", "climate regulation", "policy uncertainty", "carbon pricing"]
}


climate_keywords['Comprehensive Climate Risk and Adaptability Index'] = [
    "flood", "hurricane", "drought", "extreme heat", "storm",
    "carbon emission", "greenhouse gas", "emission intensity", "carbon dioxide", "emission reduction target",
    "climate resilience", "infrastructure upgrade", "emergency plan", "climate adaptation", "adaptation plan",
    "renewable energy", "solar power", "wind power", "low-carbon technology", "energy transition",
    "carbon tax", "emission trading", "climate regulation", "policy uncertainty", "carbon pricing"
]


def extract_keywords(text, keywords_dict):
    text = text.lower()  
    keyword_counts = {}
    
    for indicator, keywords in keywords_dict.items():
        counts = Counter()
        for keyword in keywords:
            keyword = keyword.lower()
            counts[keyword] = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
        keyword_counts[indicator] = counts
    return keyword_counts

def sentiment_analysis(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity  
    return sentiment

def quantify_indicators(keyword_counts, text, weight_keywords=0.7, weight_sentiment=0.3):
    indicators = {}
    #sentiment = sentiment_analysis(text)  
    for indicator, counts in keyword_counts.items():
        total_mentions = sum(counts.values())
        #keyword_score = total_mentions / 100  # Assume normalization factor of 100, adjust as needed
        #indicator_score = keyword_score * weight_keywords + sentiment * weight_sentiment
        indicators[indicator] = total_mentions #indicator_score
    return indicators


def plot_indicators(indicators, title, figsize=(8,6)):
    df = pd.DataFrame.from_dict(indicators, orient='index', columns=['Score'])
    #df = df.sort_values(by='Score', ascending=False)
    plt.figure(figsize=figsize)
    sns.barplot(x=df.index, y='Score', data=df, palette='viridis', hue=df.index, legend=False)
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Date')
    plt.title(title)
    plt.tight_layout()
    plt.show()


def extract_10_Q_date(text):
    date = text.split('For the quarterly period ended ')[-1].split(' Commission File')[0].split(' OR ')[0]
    return date


def process_report(html_path):
    with tqdm(total=4, desc="Processing steps", unit="step") as pbar:
        pbar.set_description("Step 1 Extracting text from HTML")
        text = extract_text_from_html(html_path)
        if not text:
            print("No text extracted from the HTML.")
            return
        pbar.update(1)
        
        pbar.set_description("Step 2 Extracting keyword counts")
        climate_keyword_counts = extract_keywords(text, climate_keywords)
        pbar.update(1)
        
        pbar.set_description("Step 3 Quantifying climate indicators")
        climate_indicators = quantify_indicators(climate_keyword_counts, text)
        pbar.update(1)
        
        pbar.set_description("Step 4 Extracting date")
        date = extract_10_Q_date(text)
        pbar.update(1)
        
    return date, climate_indicators

        # Print keyword frequencies
    # print("\n=== Climate Risk Keyword Counts ===")
    # for indicator, counts in climate_keyword_counts.items():
    #     print(f"{indicator}: {dict(counts)}")
    
    # print("\n=== Climate Risk Indicators ===")
    # for indicator, score in climate_indicators.items():
    #     print(f"{indicator}: {score:.4f}")
    # print("\n===============================")



