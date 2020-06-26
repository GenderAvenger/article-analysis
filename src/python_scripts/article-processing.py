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
import pandas as pd
def main():
    urls = article_urls(0, 1000, 39000)
    
    complete = []
    for URL in urls:
        #URL = 'https://abcnews.go.com/Politics/white-house-odd-couple-trump-boltons-tumultuous-relationship/story?id=71323127'
        article = Article(URL)
        article.download()
        article.parse()
        main_body = article.text #Main body of Article
        attempted_authors = article.authors
        sentences = sent_tokenize(main_body)

        genderize = Genderize(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
            api_key='66982c609ec00aba67eee6fb146f6210',
            timeout=30.0)

        #HTML Processing
        fp = urllib.request.urlopen(URL)
        mybytes = fp.read()

        mystr = mybytes.decode("utf8")
        fp.close()
        soup = BeautifulSoup(mystr, 'lxml')
        
        #author = author_names(attempted_authors) #Returns array of Authors through NER

        try:       
            byline = soup.find("div", class_="Byline__Author").text  #Byline through HTML 
        except:
            byline = ''
        #byline = genderize.get([author.split()[0]]) #Not working for multiple authors yet  
        authors = author_from_byline(byline)

    
        author_gender = gender_of_author(authors)
        sources= extract_sources_displacy(sentences)
        source_genders = source_gender(sources, sentences)

        
        #sources2 = extract_sources(sentences)

        count_he = source_genders.count('male')
        count_she = source_genders.count('female')

        complete_row = [article.title, authors, author_gender, sources, count_he, count_she] #Create row for article
        complete.append(complete_row)
        #write_to_json(article.title, author, gender_of_author, sources, count_he, count_she)

    complete_np = np.array(complete)
    df = pd.DataFrame(complete_np)
    df.to_csv('complete_article_data.csv')
def gender_of_author(authors):
    genderize = Genderize(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        api_key='66982c609ec00aba67eee6fb146f6210',
        timeout=30.0)
    #Return first name
    first_names = []
    for author in authors:
        first_names.append(author.split()[0])
    
    genders_full = genderize.get(first_names)
    genders =[]
    for d in genders_full:
        genders.append(d['gender'])
    return genders
def author_from_byline(byline):
    nlp = spacy.load('en_core_web_sm') #Load english
    docx = nlp(byline.lower())
    authors = []
    for ent in docx.ents:
        if ent.label_ == 'PERSON':
            authors.append(ent.text)
    return authors
def write_to_json(title, authors, gender_of_author, sources, count_male, count_female):
     #Write to JSON
        # Data to be written
        dictionary ={ 
            "title" : article.title, 
            "Author" : authors, 
            "Gender of Author": gender_of_author,
            "Sources": np.array_str(sources),
            "# of male sources" : count_male, 
            "# of female sources" : count_female
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
                #index = split_sent.index(source)
                #sources_full_name.append(split_sent[index - 1] + " " + split_sent[index])
                docx = nlp(sent)
                for ent in docx.ents:
                    if ent.label_ == 'PERSON' and source in ent.text:
                        sources_full_name.append(ent.text)
                break
    #sources_full_name = np.array(sources_full_name)
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
    
def source_gender(sources, sentences):
    nlp = spacy.load('en_core_web_sm')
    genderize = Genderize(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
            api_key='66982c609ec00aba67eee6fb146f6210',
            timeout=30.0)
    #Check for no identified sources
    if len(sources) == 0:
        genders = ['None']
    else:
        source_first_name = []
        for source in sources:
            # pronouns = []
            # #Find source in sentence
            # for i, sentence in enumerate(sentences):
            #     if source in sentences[i]:
            #         doc = nlp(sentences[i])
            #         doc_2 = nlp(sentences[i+1])
            #         for token in doc:
            #             if token.pos_ == 'PRON':
            #                 pronouns.append(token.text)
            #         for token in doc_2:
            #             if token.pos_ == 'PRON':
            #                 pronouns.append(token.text)        
            #         break
            
            source_first_name.append(source.split()[0])
        source_genders = genderize.get([source_first_name])
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


