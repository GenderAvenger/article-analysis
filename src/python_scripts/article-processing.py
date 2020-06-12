from newspaper import Article
import nltk
import spacy 
import numpy as np
import json
def main():
    URL = "https://www.cnn.com/2020/06/11/politics/trump-kamala-harris-juneteenth-tulsa-rally/index.html"

    article = Article(URL)
    article.download()
    article.parse()
    main_body = article.text #Main body of Article
    attempted_authors = article.authors
    authors = author_names(attempted_authors) #Returns array of Authors

    count_he = main_body.count(" he ") #Count number of hes
    count_she = main_body.count(" she ") #Count number of shes
    
    print(article.authors)
    print(article.publish_date)
    print(article.text)

    #Write to JSON
    # Data to be written 
    dictionary ={ 
        "title" : article.title, 
        "Author" : authors, 
        "# of \'he\'s" : count_he, 
        "# of \'she\'s" : count_she
    } 
  
    # Serializing json  
    json_object = json.dumps(dictionary, indent = 4) 
  
    # Writing to sample.json 
    with open("arti.json", "w") as outfile: 
        outfile.write(json_object) 
        
    #article.nlp()
    #print(article.keywords)
    #print(article.summary)

def author_names(attempted_authors):
    entities = []
    sp = spacy.load('en_core_web_sm') #Load english in spacy
    for author in attempted_authors:
        sen = sp(author)
        for ent in sen.ents:
            entities.append([ent.text, ent.label_])

    entities_np = np.array(entities)

    x = entities_np[:,1]
    entities_np = entities_np[entities_np[:,1]=='PERSON',:]
    authors = np.unique(entities_np)[0] #Will break with multiple authors

    return authors


if __name__ == "__main__":
    main()


