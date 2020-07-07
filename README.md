# article-analysis
Analyze the bylines and sources of news articles to see how women are represented. article-processing takes URLS of articles and outputs the bylines and sources cited in the article as well as predicted genders of these names. Data is aggregated into a csv table, an example of the output data is shown in collect

### Technologies
python 3.7.6

### Dev Environment 
You can use either a conda environment or a pip environment. 

To use a conda environment    
`conda env create -f environmemt.yml`

To use a pip environment open command line or terminal and type   
`pip install -r requirements.txt`

### Use
Open collect-articles script. Using MIT's MediaCloud Source Manager Tool look up ID for the source you are looking for. 

ABC: 39000  
NBC: 25499  
Fox: 1092  
CNN: 1095  
CBS: 1752  

For other sources check out  
https://sources.mediacloud.org/#/home 

Pass ID into article_urls() to collect URLS for analysis  
`urls = article_urls(ID)`
