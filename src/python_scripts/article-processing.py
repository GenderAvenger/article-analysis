from __future__ import print_function
from newspaper import Article
import nltk
from nltk.tokenize import sent_tokenize
from nltk.tag import StanfordNERTagger
import gender_guesser.detector as gender
import spacy 
import numpy as np
import json
import os
import itertools
import urllib

def main():
    URL = "https://www.nbcnews.com/news/us-news/how-police-killing-rayshard-brooks-could-empower-atlanta-s-citizen-n1231204"
    #nltk.download('punkt')
    gen_detect = gender.Detector() #Initialize Gender Detector
    
    article = Article(URL)
    article.download()
    article.parse()
    main_body = article.text #Main body of Article
    attempted_authors = article.authors
    authors = author_names(attempted_authors) #Returns array of Authors
    #gender_of_authors = gender_author(authors)
    gender_of_author = gen_detect.get_gender(authors.split()[0])
    count_he = main_body.count(" he ") #Count number of hes
    count_she = main_body.count(" she ") #Count number of shes
    
    sentences = sent_tokenize(main_body)
    sources = extract_sources(sentences)
    print(article.authors)
    print(article.publish_date)
    print(article.text)

    #Write to JSON
    # Data to be written 
    x = type(gender_of_author)
    y = type(sources.tostring())
    dictionary ={ 
        "title" : article.title, 
        "Author" : authors, 
        "Gender of Author": gender_of_author,
        "Sources": np.array_str(sources),
        "# of \'he\'s" : count_he, 
        "# of \'she\'s" : count_she
    } 
  
    # Serializing json  
    json_object = json.dumps(dictionary, indent = 4) 
  
    # Writing to sample.json 
    with open("example.json", "w") as outfile: 
        outfile.write(json_object) 

    #article.nlp()
    #print(article.keywords)
    #print(article.summary)
def extract_sources_stanford(sentences):
    java_path = r"C:\Program Files (x86)\Java\jre1.8.0_251\bin\java.exe"
    os.environ['JAVAHOME'] = java_path
    st = StanfordNERTagger('C:/Users/isabe/Downloads/stanford-ner-4.0.0/stanford-ner-4.0.0/classifiers/english.all.3class.distsim.crf.ser.gz', 'C:/Users/isabe/Downloads/stanford-ner-4.0.0/stanford-ner-4.0.0/stanford-ner-4.0.0.jar')
    split_text = st.tag(sentence.split()) 
def extract_sources(sentences):
    nlp = spacy.load('en_core_web_sm') #Load english in space  
    sentences_with_people = []

    for i, sentence in enumerate(sentences):
        
        sen = nlp(sentence)
        quote_bool = '"' in sentence
        quote_words_bool = ("said" or "according to" or "saying" or "say") in sentence
        k = 0
        person_found = False
        while k < len(sen.ents) and person_found == False:
            ent = sen.ents[k]
        #while sen.ents[i].label_!= 'PERSON' and quote_words_bool == False:
            if ent.label_ == 'PERSON' and quote_words_bool:
                sentences_with_people.append([sentence, ent.text])
                person_found = True
            k = k + 1
    sentences_with_people_np = np.array(sentences_with_people)
    sources = np.unique(sentences_with_people_np[:,1])

    #Remove Repeat Last Names
    for name in sources[:]:
        x = len(name.split())
        if len(name.split()) == 1:
            #sources.remove(name)
            sources = np.delete(sources, np.where(sources == name))

    return sources
    
def gender_author(authors):
    #api_key = open('AIzaSyBv4a_fpRuAaNuqj46qoyNJye4JXs6HNm0.api_key').read()
    api_key = 'AIzaSyBv4a_fpRuAaNuqj46qoyNJye4JXs6HNm0'
    query = 'Anna Bahney'
    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    params = {
        'query': query,
        'limit': 10,
        'indent': True,
        'key': api_key,
    }
    url = service_url + '?' + urllib.parse.urlencode(params)
    response = json.loads(urllib.request.urlopen(url).read())
    for element in response['itemListElement']:
        x = element
        print(element['result']['name'] + ' (' + str(element['resultScore']) + ')')
        #print(element['result']['gender'])
    
def author_names(attempted_authors):
    entities = []
    sp = spacy.load('en_core_web_sm') #Load english in spacy
    for author in attempted_authors:
        sen = sp(author)
        x = sen.ents
        for ent in sen.ents:
            entities.append([ent.text, ent.label_])

    entities_np = np.array(entities)

    x = entities_np[:,1]
    entities_np = entities_np[entities_np[:,1]=='PERSON',:]
    authors = np.unique(entities_np)[0] #Will break with multiple authors

    return authors


if __name__ == "__main__":
    main()


