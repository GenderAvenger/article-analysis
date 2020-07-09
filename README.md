# article-analysis
Analyze news articles by extracting bylines and sources to see how women are represented

# Technology
Python 3.7.6  
MediaCloud API  

# Dev Environment
To set up the development environment use either:  
`pip install -r requirements.txt`  

`conda env create -f analysis_2.yml`

# Usage
Use MediaCloud to identify the ID of the source that you want to analyze articles from. Open article-analysis.py and pass in the ID  
`urls = article_urls(ID)`

Find ID of source by searching up on MediaCloud's Source Manager  
https://sources.mediacloud.org/#/home
