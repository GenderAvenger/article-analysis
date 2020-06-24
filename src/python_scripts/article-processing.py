from __future__ import print_function
from newspaper import Article
from genderize import Genderize
import nltk
from nltk.tokenize import sent_tokenize
import gender_guesser.detector as gender
import spacy 
import numpy as np
import json
import os
import itertools
import string
import urllib
import requests, mediacloud.api
from collect_articles import article_urls
from bs4 import BeautifulSoup
import re

def main():
    urls = article_urls(0, 1000, 39000)
    for URL in urls:
        #URL = 'https://abcnews.go.com/Politics/white-house-odd-couple-trump-boltons-tumultuous-relationship/story?id=71323127'
        article = Article(URL)
        article.download()
        article.parse()
        main_body = article.text #Main body of Article
        attempted_authors = article.authors

        #HTML Processing
        fp = urllib.request.urlopen(URL)
        mybytes = fp.read()

        mystr = mybytes.decode("utf8")
        fp.close()
        soup = BeautifulSoup(mystr, 'lxml')
        author = soup.find("div", class_="Byline__Author").text #Byline through HTML 

        authors = author_names(attempted_authors) #Returns array of Authors through NER
        gender_of_author = Genderize().get([authors.split()[0]])
        sentences = sent_tokenize(main_body)
        sources2 = extract_sources(sentences)
        sources= extract_sources_displacy(sentences)
        source_genders = source_gender(sources)
        
        count_he = source_genders.count('male')
        count_she = source_genders.count('female')
      
        #Write to JSON
        # Data to be written
        dictionary ={ 
            "title" : article.title, 
            "Author" : authors, 
            "Gender of Author": gender_of_author,
            "Sources": np.array_str(sources),
            "# of male sources" : count_he, 
            "# of female sources" : count_she
        } 
    
        # Serializing json  
        json_object = json.dumps(dictionary, indent = 4) 
    
        # Writing to sample.json 
        with open("example.json", "w") as outfile: 
            outfile.write(json_object) 

def extract_sources_stanford(sentences):
    java_path = r"C:\Program Files (x86)\Java\jre1.8.0_251\bin\java.exe"
    os.environ['JAVAHOME'] = java_path
    st = StanfordNERTagger('C:/Users/isabe/Downloads/stanford-ner-4.0.0/stanford-ner-4.0.0/classifiers/english.all.3class.distsim.crf.ser.gz', 'C:/Users/isabe/Downloads/stanford-ner-4.0.0/stanford-ner-4.0.0/stanford-ner-4.0.0.jar')
    split_text = st.tag(sentence.split()) 

def extract_sources_displacy(sentences):
    nlp = spacy.load('en_core_web_sm') #Load english
    sources = []
    for i, sentence in enumerate(sentences):
        quote_words_bool = ("said" or "according to" or "saying" or "say" or "says") in sentence
        sen = nlp(sentence)
        if quote_words_bool:
            #Merge noun chunks
            #for noun_phrase in list(sen.noun_chunks):
                #noun_phrase.merge(noun_phrase.root.tag_,noun_phrase.root.lemma_, noun_phrase.root.ent_type_)
            #Find verb signifier
            for token in sen:
                if token.text == "said" or "according to " or "saying" or "say" or "says":
                    for a in token.children:
                        if a.dep_ == 'nsubj' and a.pos_ == 'PROPN':
                            sources.append(a.text)
    sources = np.array(sources)
    sources = np.unique(sources) #Remove duplicates

    #Remove non-names
    for name in sources[:]:
        if name.islower() or any(p in name for p in string.punctuation):
            sources = np.delete(sources, np.where(sources == name))

    #Find full names
    sources_full_name = []
    for source in sources:      
        for sent in sentences:
            split_sent = re.findall(r"[\w']+|[.,!?;]", sent)
            if source in split_sent:
                #split_sent = sent.split() #Split sentence into list
                index = split_sent.index(source)
                sources_full_name.append(split_sent[index - 1] + " " + split_sent[index])
                break
    sources_full_name = np.array(sources_full_name)
    return sources_full_name 
           

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
    sources = np.array(sentences_with_people)

    #Check for empty array
    if len(sources) == 0:
        return sources
    
    sources = np.unique(sources[:,1]) #Remove repeats

    #Remove Repeat Last Names
    for name in sources[:]:
        x = len(name.split())
        if len(name.split()) == 1:
            sources = np.delete(sources, np.where(sources == name))

    return sources
    
def source_gender(sources):
    #Check for no identified sources
    if len(sources) == 0:
        genders = ['None']
    else:
        source_first_name = []
        for source in sources:
            source_first_name.append(source.split()[0])
        source_genders = Genderize().get([source_first_name])
        genders =[]
        for d in source_genders:
            genders.append(d['gender'])

    return genders
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


