# -*- coding: utf-8 -*-

from google.colab import drive
drive.mount('/content/drive')

# import spacy
import spacy

# load english language model
nlp = spacy.load('en_core_web_sm',disable=['ner','textcat'])

text = "This is a sample sentence."

# create spacy 
doc = nlp(text)

for token in doc:
    print(token.text,'->',token.pos_)

"""We were easily able to determine the POS tags of all the words in the sentence. But how does it help in Information Extraction? 

Well, if we wanted to extract nouns from the sentences, we could take a look at POS tags of the words/tokens in the sentence, using the attribute **.pos_**, and extract them accordingly.
"""

for token in doc:
    # check token pos
    if token.pos_=='NOUN':
        # print token
        print(token.text)

"""But sometimes extracting information purely based on the POS tags is not enough. 
For the sentence below:
"""

text = "The children love cream biscuits"

# create spacy 
doc = nlp(text)

for token in doc:
    print(token.text,'->',token.pos_)

"""If I wanted to extract the subject and the object from a sentence, I can’t do that based on their POS tags. For that, I need to look at how these words are related to each other. These are called **Dependencies**.

We can make use of [spaCy’s displacy](https://explosion.ai/demos/displacy) visualizer that displays the word dependencies in a graphical manner:
"""

from spacy import displacy 
displacy.render(doc, style='dep',jupyter=True)

"""Pretty cool! This directed graph is known as a [dependency graph](https://www.analyticsvidhya.com/blog/2017/12/introduction-computational-linguistics-dependency-trees/). It represents the relations between different words of a sentence.

Each word is a **node** in the Dependency graph. The relationship between words is denoted by the edges. For example, “The” is a determiner here, “children” is the subject of the sentence, “biscuits” is the object of the sentence, and “cream” is a compound word that gives us more information about the object.

The arrows carry a lot of significance here:

- The **arrowhead** points to the words that are **dependent** on the word pointed by the **origin of the arrow**
- The former is referred to as the **child node** of the latter. For example, “children” is the child node of “love”
- The word which has no incoming arrow is called the **root node** of the sentence

Let’s see how we can extract the subject and the object from the sentence. Like we have an attribute for POS in SpaCy tokens, we similarly have an attribute for extracting the dependency of a token denoted by dep_:
"""

for token in doc:
    # extract subject
    if (token.dep_=='nsubj'):
        print(token.text)
    # extract object
    elif (token.dep_=='dobj'):
        print(token.text)

"""Voila! We have the subject and object of our sentence.

Using POS tags and Dependency tags, we can look for relationship between different entities in a sentence. For example, in the sentence "The **cat** perches **on** the **window sill**", we have two noun entities,"cat" and "window sill", related by the preposition "on". We can look for such relationships and much more to extract meaningful information from our text data.

*I suggest going through [this amazing blog](https://www.analyticsvidhya.com/blog/2019/09/introduction-information-extraction-python-spacy/) which explains Information Extraction with tons of examples.*

# Where Do We Go from Here?

We have briefly spoken about the theory regarding Information Extraction which I believe is important to understand before jumping into the crux of this article.

`“An ounce of practice is generally worth more than a ton of theory.” –E.F. Schumacher`

In the following sections, I am going to explore a text dataset and apply the information extraction technique to retrieve some important information, understand the structure of the sentences, and the relationship between entities.

So, without further ado, let’s get cracking on the code!

# Getting Familiar with the Dataset

The dataset we are going to be working with is the [United Nations General Debate Corpus](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/0TJX8Y). It contains speeches made by representatives of all the member countries from the year 1970 to 2018 at the General Debate of the annual session of United Nations General Assembly. 

But we will take a subset of this dataset and work with speeches made by India at these debates. This will allow us to stay on track and better understand the task at hand of understanding Information Extraction. This leaves us with 49 speeches made by India over the years, each speech ranging from anywhere between 2000 to 6000+ words.

Having said that, let’s have a look at our dataset:
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import re

# Folder path
folders = glob.glob('/content/drive/MyDrive/Converted sessions/Session*')

# Dataframe
df = pd.DataFrame(columns={'Country','Speech','Session','Year'})

# Read speeches by India
i = 0 
for file in folders:
    
    speech = glob.glob(file+'/IND*.txt')
    if len(speech)<1: continue
    with open(speech[0],encoding='utf8') as f:
        # Speech
        df.loc[i,'Speech'] = f.read()
        # Year 
        df.loc[i,'Year'] = speech[0].split('_')[-1].split('.')[0]
        # Session
        df.loc[i,'Session'] = speech[0].split('_')[-2]
        # Country
        df.loc[i,'Country'] = speech[0].split('_')[0].split("/")[-1]
        # Increment counter
        i += 1 
        
df.head()

"""Snapshot of one of the speeches:"""

df.loc[0,'Speech']

"""Now let's start working with out dataset!

# Speech Text Pre-Processing

First, we need to clean the text data. Each paragraph in the speech was numbered to distinctly identify it. 

There are unwanted characters like newline character, a hyphen, salutations, and apostrophes, like in any other text dataset.
Also references made in each speech to other documents is not required

<!-- I have written a simple function to clean the speeches. **An important point here is that I haven’t used lemmatization or changed the words to lowercase as it has the potential to change the POS tag of the word.** We certainly don’t want to do that as you will see in the upcoming subsections. -->
"""

# function to preprocess speech
def clean(text):
    
    # removing paragraph numbers
    text = re.sub('[0-9]+.\t','',str(text))
    # removing new line characters
    text = re.sub('\n ','',str(text))
    text = re.sub('\n',' ',str(text))
    # removing apostrophes
    text = re.sub("'s",'',str(text))
    # removing hyphens
    text = re.sub("-",' ',str(text))
    text = re.sub("— ",'',str(text))
    # removing quotation marks
    text = re.sub('\"','',str(text))
    # removing salutations
    text = re.sub("Mr\.",'Mr',str(text))
    text = re.sub("Mrs\.",'Mrs',str(text))
    # removing any reference to outside text
    text = re.sub("[\(\[].*?[\)\]]", "", str(text))
    
    return text

# preprocessing speeches
df['Speech_clean'] = df['Speech'].apply(clean)

"""# Split the Speech into Different Sentences

Spliting our speeches into separate sentences will allow us to extract information from each sentence and later we can combine it to get cummulative information from any specific year.
"""

# split sentences
def sentences(text):
    # split sentences and questions
    text = re.split('[.?]', text)
    clean_sent = []
    for sent in text:
        clean_sent.append(sent)
    return clean_sent

# sentences
df['sent'] = df['Speech_clean'].apply(sentences)

df.head()

"""Finally, create a dataframe containing the sentences from different years:"""

# Create a dataframe containing sentences
df2 = pd.DataFrame(columns=['Sent','Year','Len'])

# List of sentences for new df
row_list = []

# for-loop to go over the df speeches
for i in range(len(df)):
    
    # for-loop to go over the sentences in the speech
    for sent in df.loc[i,'sent']:
        
        wordcount = len(sent.split())  # Word count
        year = df.loc[i,'Year']  # Year
        dict1 = {'Year':year,'Sent':sent,'Len':wordcount}  # Dictionary
        row_list.append(dict1)  # Append dictionary to list
    
# Create the new df
df2 = pd.DataFrame(row_list)

df2.head()

df2.shape

"""After performing this operation, we end up with 7150 sentences. 
<!-- Going over them and extracting information manually will be a difficult task. That’s why we are looking at Information Extraction using NLP techniques! -->

# Information Extraction using SpaCy
"""

!pip install visualise-spacy-tree

import spacy
from spacy.matcher import Matcher 

from spacy import displacy 
import visualise_spacy_tree
from IPython.display import Image, display

# load english language model
nlp = spacy.load('en_core_web_sm',disable=['ner','textcat'])

"""We will need the spaCy Matcher class to create a pattern to match phrases in the text. We’ll also require the displaCy module for visualizing the dependency graph of sentences.

The **visualise_spacy_tree** library will be needed for creating a tree-like structure out of the Dependency graph. This helps in visualizing the graph in a better way. Finally, IPython Image and display classes are required to output the tree.

## Information Extraction #1 – Finding Mentions of Prime Minister in the Speech

Many of the speeches referred to what the Prime Minister had said, thought or achieved in the past. So we extract those sentences from the speeches that referred to Prime Ministers of India, and try and understand what their thinking and perspective was, and also try to unravel any common or differing beliefs over the years.

To achieve this task, We used Spacy's Matcher class. It allows you to match a sequence of words based on certain patterns. For the current task, we know that whenever a Prime Minister is reffered to in the speech, it will be in one of the following ways:
* Prime Minister of [Country] ...
* Prime Minister [Name] ...

Using this general understanding one came up with a pattern as follows:

pattern = [
  
      {'LOWER':'prime'},

      {'LOWER':'minister'},
        
      {'POS':'ADP','OP':'?'},
        
      {'POS':'PROPN'}]
        
    
* Here, each dictionary in the list is a unique word. 
* The first and second words match the keyword "Prime Minister" irrespective of whether it is in uppercase or not.
* The third keyword matches a word that is a preposition, specifically we need "of". But it may or may not be present in the pattern, therefore, an additional key, "OP", is mentioned to point out just that.
* Finally, the last keyword in the phrase should be a proper noun. This is either be the name of the country or name of the prime minister.
* The matched keywords have to be in continuation otherwise the pattern will not match the phrase.
"""

# Function to find sentences containing PMs of India
def find_names(text):
    
    names = []
    
    # Create a spacy doc
    doc = nlp(text)
    
    # Define the pattern
    pattern = [{'LOWER':'prime'},
              {'LOWER':'minister'},
              {'POS':'ADP','OP':'?'},
              {'POS':'PROPN'}]
                
    # Matcher class object 
    matcher = Matcher(nlp.vocab) 
    matcher.add("names", None, pattern) 

    matches = matcher(doc)

    # Finding patterns in the text
    for i in range(0,len(matches)):
        
        # match: id, start, end
        token = doc[matches[i][1]:matches[i][2]]
        # append token to list
        names.append(str(token))
    
    # Only keep sentences containing Indian PMs
    for name in names:
        if (name.split()[2] == 'of') and (name.split()[3] != "India"):
                names.remove(name)
            
    return names

# Apply function
df2['PM_Names'] = df2['Sent'].apply(find_names)

"""Here are some sample sentences from the year 1984 that matched our pattern:"""

# look at sentences for a specific year
for i in range(len(df2)):
    if df2.loc[i,'Year'] in ['1984']:
        if len(df2.loc[i,'PM_Names'])!=0:
            print('->',df2.loc[i,'Sent'],'\n')

count=0
for i in range(len(df2)):
    if len(df2.loc[i,'PM_Names'])!=0:
        count+=1
print(count)

"""58 sentences out of 7150 total sentences gave an output that matched our pattern. 

<!-- I have summarised the relevant information from these outputs here:

- PM Indira Gandhi and PM Jawaharlal Nehru believed in working together in unity and with the principles of the UN
- PM Indira Gandhi believed in striking a balance between global production and consumption. She set out policies dedicated to national reconstruction and the consolidation of a secular and pluralistic political system
- PM Indira Gandhi emphasized that India does not intervene in the internal affairs of other countries. However, this stand on foreign policy took a U-turn under PM Rajiv Gandhi when he signed an agreement with the Sri Lankan Prime Minister which brought peace to Sri Lanka
- Both PM Indira Gandhi and PM Rajiv Gandhi believed in the link between economic development and protection of the environment
- PM Rajiv Gandhi advocated for the disarmament of nuclear weapons, a belief that was upheld by India over the years
- Indian, under different PMs, has always extended a hand of peace towards Pakistan over the years
- PM Narendra Modi believes that economic empowerment and upliftment of any nation involves the empowerment of its women
- PM Narendra Modi has launched several schemes that will help India achieve its SGD goals

Using information extraction, we were able to isolate only a few sentences that we required that gave us maximum results. -->

## Information Extraction #2 – Finding Initiatives

There were a lot of initiatives, schemes, agreements, conferences, programs, etc. that were mentioned in the speeches. For example, ‘Paris agreement’, ‘Simla Agreement’, ‘Conference on Security Council’, ‘Conference of Non Aligned Countries’, ‘International Solar Alliance’, ‘Skill India initiative’, etc.

Extracting these would give us an idea about what are the priorities for India and whether there is a pattern as to why they are mentioned quite often in the speeches.

We are refering all the schemes, initiatives, conferences, programmes, etc. keywords as initiatives.

To extract initiatives from the text, we identify those sentences that talk about the initiatives. We use simple regex to select only those sentences that contain the keyword ‘initiative’, ‘scheme’, ‘agreement’, etc. This will reduce our search for the initiative pattern that we are looking for:
"""

# Function to check if keyswords like 'programs','schemes', etc. present in sentences

def prog_sent(text):
    
    patterns = [r'\b(?i)'+'plan'+r'\b',
               r'\b(?i)'+'programme'+r'\b',
               r'\b(?i)'+'scheme'+r'\b',
               r'\b(?i)'+'campaign'+r'\b',
               r'\b(?i)'+'initiative'+r'\b',
               r'\b(?i)'+'conference'+r'\b',
               r'\b(?i)'+'agreement'+r'\b',
               r'\b(?i)'+'alliance'+r'\b']

    output = []
    flag = 0
    
    # Look for patterns in the text
    for pat in patterns:
        if re.search(pat, text) != None:
            flag = 1
            break
    return flag 

# Apply function
df2['Check_Schemes'] = df2['Sent'].apply(prog_sent)

# Sentences that contain the initiative words
count = 0
for i in range(len(df2)):
    if df2.loc[i,'Check_Schemes'] == 1:
        count+=1
print(count)

"""Not all of these will contain the initiative name. Some of these might be generally talking about initiatives but no initiative name might be present in them.

Therefore, we need to extract only those sentences that contain the initiative names. For that, we use the spaCy Matcher to come up with a pattern that matches these initiatives.

The initiative name is a proper noun that starts with a determiner and ends with either ‘initiative’/’programme’/’agreement’ etc. words in the end. It also includes an occasional preposition in the middle. Most of the initiative names were between two to five words long.
"""

# To extract initiatives using pattern matching
def all_schemes(text,check):
    
    schemes = []
    
    doc = nlp(text)
    
    # Initiatives keywords
    prog_list = ['programme','scheme',
                 'initiative','campaign',
                 'agreement','conference',
                 'alliance','plan']
    
    # Define pattern to match initiatives names 
    pattern = [{'POS':'DET'},
               {'POS':'PROPN','DEP':'compound'},
               {'POS':'PROPN','DEP':'compound'},
               {'POS':'PROPN','OP':'?'},
               {'POS':'PROPN','OP':'?'},
               {'POS':'PROPN','OP':'?'},
               {'LOWER':{'IN':prog_list},'OP':'+'}
              ]
    
    if check == 0:
        # return blank list
        return schemes

    # Matcher class object 
    matcher = Matcher(nlp.vocab) 
    matcher.add("matching", None, pattern) 
    matches = matcher(doc)

    for i in range(0,len(matches)):
        
        # match: id, start, end
        start, end = matches[i][1], matches[i][2]
        
        if doc[start].pos_=='DET':
            start = start+1
        
        # matched string
        span = str(doc[start:end])
        
        if (len(schemes)!=0) and (schemes[-1] in span):
            schemes[-1] = span
        else:
            schemes.append(span)
        
    return schemes

# apply function
df2['Schemes1'] = df2.apply(lambda x:all_schemes(x.Sent,x.Check_Schemes),axis=1)

"""Lets see how many of the sentences contain an initiative name."""

count = 0
for i in range(len(df2)):
    if len(df2.loc[i,'Schemes1'])!=0:
        count+=1
print(count)

year = '2018'
for i in range(len(df2)):
    if df2.loc[i,'Year']==year:
        if len(df2.loc[i,'Schemes1'])!=0:
            print('->',df2.loc[i,'Year'],',',df2.loc[i,'Schemes1'],':')
            print(df2.loc[i,'Sent'])

"""A lot more initiatives in the speeches that did not match our pattern. For example, in the year 2018, there were other initiatives too like “MUDRA”, ”Ujjwala”, ”Paris Agreement”, etc. 

To understand the structure of the sentence we print the dependency graph of a sample example but in a tree fashion which gives a better intuition of the structure.
"""

# Printing dependency tree
doc = nlp(' Last year, I spoke about the Ujjwala programme , through which, I am happy to report, 50 million free liquid-gas connections have been provided so far')
png = visualise_spacy_tree.create_png(doc)
display(Image(png))

"""See how 'Ujjwala' is a child node of 'programme'. Have a look at another example."""

doc = nlp('Prime Minister Modi, together with the Prime Minister of France, launched the International Solar Alliance')
png = visualise_spacy_tree.create_png(doc)
display(Image(png))

"""Basic idea is that the initiative names are usually children of nodes that containing words like 'initiative','programme',etc. Based on this knowledge we can develop our own rule. 

Rule:
* Look for tokens in sentences that contain initiative keywords. 
* Look at its subtree (or words dependent on it) using *token.subtree* and extract only those nodes/words that are proper nouns, since they are most likely going to contain the name of the initiative.
"""

# rule to extract initiative name
def sent_subtree(text):
    
    # pattern match for schemes or initiatives
    patterns = [r'\b(?i)'+'plan'+r'\b',
           r'\b(?i)'+'programme'+r'\b',
           r'\b(?i)'+'scheme'+r'\b',
           r'\b(?i)'+'campaign'+r'\b',
           r'\b(?i)'+'initiative'+r'\b',
           r'\b(?i)'+'conference'+r'\b',
           r'\b(?i)'+'agreement'+r'\b',
           r'\b(?i)'+'alliance'+r'\b']
    
    schemes = []
    doc = nlp(text)
    flag = 0
    # if no initiative present in sentence
    for pat in patterns:
        
        if re.search(pat, text) != None:
            flag = 1
            break
    
    if flag == 0:
        return schemes

    # iterating over sentence tokens
    for token in doc:

        for pat in patterns:
                
            # if we get a pattern match
            if re.search(pat, token.text) != None:

                word = ''
                # iterating over token subtree
                for node in token.subtree:
                    # only extract the proper nouns
                    if (node.pos_ == 'PROPN'):
                        word += node.text+' '

                if len(word)!=0:
                    schemes.append(word)

    return schemes      

# derive initiatives
df2['Schemes2'] = df2['Sent'].apply(sent_subtree)

count = 0
for i in range(len(df2)):
    if len(df2.loc[i,'Schemes2'])!=0:
        count+=1
print(count)

"""**Sample 2018 output**"""

year = '2018'
for i in range(len(df2)):
    if df2.loc[i,'Year']==year:
        if len(df2.loc[i,'Schemes2'])!=0:
            print('->',df2.loc[i,'Year'],',',df2.loc[i,'Schemes2'],':')
            print(df2.loc[i,'Sent'])

"""summary:

* There are a lot of different international initiatives or schemes that India has mentioned in its speeches. This goes to show that India has been an active member of the international community working towards building a better future by solving problems through these intiavtives. 

* Another point to highlight here is that the initiatives mentioned in the initial years have been more focused on those that concern the international coomunity. However, during recent times, especially after 2014, a lot of domestic initiatives have been mentioned in the speeches like 'Ayushman Bharat', 'Pradhan Mantri Jan Dhan Yojana', etc. This shows a shift in how the country percevies its role in the community. By mentioning a lot of domestic initiatives, India has started to put more of the domestic work in front of the international community to witness and, probably, even follow in their footsteps.

## Finding Patterns in the Speeches
"""

plt.hist(df2['Len'],bins=20,range=[0,100])
plt.xticks(np.arange(0,100,5));

"""Looking at the histogram, we can see that most of the sentences range from 15-20 words. So I am going to work with sentences that have no more than 15 words."""

row_list = []
# df2 contains all sentences from all speeches
for i in range(len(df2)):
    sent = df2.loc[i,'Sent']
    
    if (',' not in sent) and (len(sent.split()) <= 15):
        
        year = df2.loc[i,'Year']
        length = len(sent.split())
        
        dict1 = {'Year':year,'Sent':sent,'Len':length}
        row_list.append(dict1)
        
# df with shorter sentences
df3 = pd.DataFrame(columns=['Year','Sent',"Len"])
df3 = pd.DataFrame(row_list)

df3.head()

"""Now, lets come up with a function that will generate random sentences from this dataframe. """

from random import randint
def rand_sent(df):
    
    index = randint(0, len(df))
    print('Index = ',index)
    doc = nlp(df.loc[index,'Sent'][1:])
    displacy.render(doc, style='dep',jupyter=True)
    
    return index

rand_sent(df3)

"""Finally, let's make a fucntion to evaluate the result of our rule."""

# function to check output percentage for a rule
def output_per(df,out_col):
    
    result = 0
    
    for out in df[out_col]:
        if len(out)!=0:
            result+=1
    
    per = result/len(df)
    per *= 100
    
    return per

"""Right, let's get down to the business of making some rules!

## Information Extraction #3 – Rule on Noun-Verb-Noun Phrases

When we look at a sentence, it generally contains a **subject(noun), action(verb) and an object(noun)**. Rest of the words are just there to give us additional information about the entities. Therefore, we leverage this basic structure to extract the main bits of information from the sentence. Take for example the following sentence:
"""

# To download dependency graphs to local folder
from pathlib import Path

text = df3.loc[9,'Sent'][1:]

doc = nlp(text)
img = displacy.render(doc, style='dep',jupyter=True)
img

# To save to folder
# output_path = Path("./img1.svg")
# output_path.open("w", encoding="utf-8").write(img)

"""What will be extracted is "countries face threats", which should give us a fair idea about what the sentence is trying to say.

So lets look at how this rule fairs what we run it against the short sentences that are working with.
"""

# Function for rule 1: noun(subject), verb, noun(object)
def rule1(text):
    
    doc = nlp(text)
    
    sent = []
    
    for token in doc:
        
        # If the token is a verb
        if (token.pos_=='VERB'):
            
            phrase =''
            
            # Only extract noun or pronoun subjects
            for sub_tok in token.lefts:
                
                if (sub_tok.dep_ in ['nsubj','nsubjpass']) and (sub_tok.pos_ in ['NOUN','PROPN','PRON']):
                    
                    # Add subject to the phrase
                    phrase += sub_tok.text

                    # Save the root of the word in phrase
                    phrase += ' '+token.lemma_ 

                    # Check for noun or pronoun direct objects
                    for sub_tok in token.rights:
                        
                        # Save the object in the phrase
                        if (sub_tok.dep_ in ['dobj']) and (sub_tok.pos_ in ['NOUN','PROPN']):
                                    
                            phrase += ' '+sub_tok.text
                            sent.append(phrase)
            
    return sent

# Create a df containing sentence and its output for rule 1
row_list = []

for i in range(len(df3)):
    
    sent = df3.loc[i,'Sent']
    year = df3.loc[i,'Year']
    output = rule1(sent)
    dict1 = {'Year':year,'Sent':sent,'Output':output}
    row_list.append(dict1)
    
df_rule1 = pd.DataFrame(row_list)

# Rule 1 achieves 20% result on simple sentences
output_per(df_rule1,'Output')

"""We are getting more than 20% pattern match for our rule, we can check it for all the sentences in the corpus."""

# Create a df containing sentence and its output for rule 1
row_list = []

# df2 contains all the sentences from all the speeches
for i in range(len(df2)):
    
    sent = df2.loc[i,'Sent']
    year = df2.loc[i,'Year']
    output = rule1(sent)
    dict1 = {'Year':year,'Sent':sent,'Output':output}
    row_list.append(dict1)
    
df_rule1_all = pd.DataFrame(row_list)

# Check rule1 output on complete speeches
output_per(df_rule1_all,'Output')

"""We are getting more than a 30% match for our rules, which means 2226 out of 7150 sentences matched this pattern. Form a new dataframe containing only those sentences that have an output and then segregate the verb from the nouns:"""

# selecting non-empty output rows
df_show = pd.DataFrame(columns=df_rule1_all.columns)

for row in range(len(df_rule1_all)):
    
    if len(df_rule1_all.loc[row,'Output'])!=0:
        df_show = df_show.append(df_rule1_all.loc[row,:])

# reset the index
df_show.reset_index(inplace=True)
df_show.drop('index',axis=1,inplace=True)

df_rule1_all.shape, df_show.shape

# separate subject, verb and object

verb_dict = dict()
dis_dict = dict()
dis_list = []

# iterating over all the sentences
for i in range(len(df_show)):
    
    # sentence containing the output
    sentence = df_show.loc[i,'Sent']
    # year of the sentence
    year = df_show.loc[i,'Year']
    # output of the sentence
    output = df_show.loc[i,'Output']
    
    # iterating over all the outputs from the sentence
    for sent in output:
        
        # separate subject, verb and object
        n1 = sent.split()[:1]
        v = sent.split()[1]
        n2 = sent.split()[2:]
        
        # append to list, along with the sentence
        dis_dict = {'Sent':sentence,'Year':year,'Noun1':n1,'Verb':v,'Noun2':n2}
        dis_list.append(dis_dict)
        
        # counting the number of sentences containing the verb
        verb = sent.split()[1]
        if verb in verb_dict:
            verb_dict[verb]+=1
        else:
            verb_dict[verb]=1

df_sep = pd.DataFrame(dis_list)

"""We can seperate the verb from the subject noun and object noun. This will allows us to better analyse the result."""

df_sep.head()

"""Top occuring verbs used in the sentences."""

sort = sorted(verb_dict.items(), key = lambda d:(d[1],d[0]), reverse=True)
# top 10 most used verbs in sentence
sort[:10]

"""We look at specific verbs to see what kind of information is prsent. For example 'welcome' and 'support' could tell us what India encourages. And verbs like 'face' could maybe tell use what kind of problems we face in the real world."""

# support verb
df_sep[df_sep['Verb']=='support']

# face
df_sep[df_sep['Verb']=='face']

"""By looking at the output, we can try to make out what is the context of the sentence. For example, we can see that India supports ‘efforts’, ‘viewpoints’, ‘initiatives’, ‘struggles’, ‘desires, ‘aspirations’, etc. While India believes that the world faces ‘threat’, ‘conflicts’, ‘colonialism’, ‘pandemics’, etc.

## Information Extraction #4 – Rule on Adjective Noun Structure

Many nouns have an adjective or a word with a compound dependency that augments the meaning of a noun. Extracting these along with the noun will give us better information about the subject and the object.

Example:
"""

text = 'Our people are expecting a better life.'
print(text)
doc = nlp(text)
img = displacy.render(doc, style='dep',jupyter=True)
img

#output_path = Path("./img2.svg")
#output_path.open("w", encoding="utf-8").write(img)

"""What we are looking to achieve here is: "people","expecting" and "better life".

Rules:
* We look for tokens that have a Noun POS tag and have subject or object dependency
* Then we look at the child nodes of these tokens and append it to the phrase only if it modifies the noun
"""

# function for rule 2
def rule2(text):
    
    doc = nlp(text)

    pat = []
    
    # iterate over tokens
    for token in doc:
        phrase = ''
        # if the word is a subject noun or an object noun
        if (token.pos_ == 'NOUN')\
            and (token.dep_ in ['dobj','pobj','nsubj','nsubjpass']):
            
            # iterate over the children nodes
            for subtoken in token.children:
                # if word is an adjective or has a compound dependency
                if (subtoken.pos_ == 'ADJ') or (subtoken.dep_ == 'compound'):
                    phrase += subtoken.text + ' '
                    
            if len(phrase)!=0:
                phrase += token.text
             
        if  len(phrase)!=0:
            pat.append(phrase)
        
    
    return pat

# Create a df containing sentence and its output for rule 2
row_list = []

for i in range(len(df3)):
    
    sent = df3.loc[i,'Sent']
    year = df3.loc[i,'Year']
    # Rule 2
    output = rule2(sent)
    
    dict1 = {'Year':year,'Sent':sent,'Output':output}
    row_list.append(dict1)

df_rule2 = pd.DataFrame(row_list)

df_rule2.head()

# Rule 2 output
output_per(df_rule2,'Output')

"""51% of the short sentences match this rule. We can try now check it on the entire corpus."""

# create a df containing sentence and its output for rule 2
row_list = []

# df2 contains all the sentences from all the speeches
for i in range(len(df2)):
    
    sent = df2.loc[i,'Sent']
    year = df2.loc[i,'Year']
    output = rule2(sent)
    dict1 = {'Year':year,'Sent':sent,'Output':output}
    row_list.append(dict1)
    
df_rule2_all = pd.DataFrame(row_list)

# check rule output on complete speeches
output_per(df_rule2_all,'Output')

df_rule2_all.head(10)

"""Out of 7150, 5470 sentences matched our pattern rule."""

# Selecting non-empty outputs
df_show2 = pd.DataFrame(columns=df_rule2_all.columns)

for row in range(len(df_rule2_all)):
    
    if len(df_rule2_all.loc[row,'Output'])!=0:
        df_show2 = df_show2.append(df_rule2_all.loc[row,:])

# Reset the index
df_show2.reset_index(inplace=True)
df_show2.drop('index',axis=1,inplace=True)

df_show2.head(10)

df_rule2_all.shape,df_show2.shape

"""Now we can combine this rule along with the rule that we created previously. This will give us a better perspective of what information in present in a sentence."""

def rule2_mod(text,index):
    
    doc = nlp(text)

    phrase = ''
    
    for token in doc:
        
        if token.i == index:
            
            for subtoken in token.children:
                if (subtoken.pos_ == 'ADJ'):
                    phrase += ' '+subtoken.text
            break
    
    return phrase

# rule 1 modified function
def rule1_mod(text):
    
    doc = nlp(text)
    
    sent = []
    
    for token in doc:
        # root word
        if (token.pos_=='VERB'):
            
            phrase =''
            
            # only extract noun or pronoun subjects
            for sub_tok in token.lefts:
                
                if (sub_tok.dep_ in ['nsubj','nsubjpass']) and (sub_tok.pos_ in ['NOUN','PROPN','PRON']):
                        
                    adj = rule2_mod(text,sub_tok.i)
                    
                    phrase += adj + ' ' + sub_tok.text

                    # save the root word of the word
                    phrase += ' '+token.lemma_ 

                    # check for noun or pronoun direct objects
                    for sub_tok in token.rights:
                        
                        if (sub_tok.dep_ in ['dobj']) and (sub_tok.pos_ in ['NOUN','PROPN']):
                             
                            adj = rule2_mod(text,sub_tok.i)
                            
                            phrase += adj+' '+sub_tok.text
                            sent.append(phrase)
            
    return sent

# create a df containing sentence and its output for modified rule 1
row_list = []

# df2 contains all the sentences from all the speeches
for i in range(len(df2)):
    
    sent = df2.loc[i,'Sent']
    year = df2.loc[i,'Year']
    output = rule1_mod(sent)
    dict1 = {'Year':year,'Sent':sent,'Output':output}
    row_list.append(dict1)
    
df_rule1_mod_all = pd.DataFrame(row_list)
# check rule1 output on complete speeches
output_per(df_rule1_mod_all,'Output')

df_rule1_mod_all.head(20)

"""## Information Extraction #5 – Rule on Prepositions

Thank god for preposistions. They tell us where or when something is in relationship with something else. For example, *The people **of** India believe **in** the priciples **of** United Nations.*. Clearly extarcting phrases inclusing prepositions will give us a lot of information from the sentence. This is exactly what we are going to achieve with this rule.

Let's try to understand how this rule works by going over it on a sample sentece - "India has once again shown faith in democracy."

* We iterate over all the tokens looking for prepositions. For example *in* in this sentence.
* On encountering a preposition, we check if it has a head word that is a noun. For example the word *faith* in this sentence.
* Then we look at the child tokens of the preposition token falling on its right side. For example, the word *democracy*.

This should finally extract the phrase *faith in democracy* from the sentence. Have a look at the dependency graph of the sentence below.
"""

text = "India has once again shown faith in democracy."
print(text)
doc = nlp(text)
img = displacy.render(doc, style='dep',jupyter=True)
img

#output_path = Path("./img3.svg")
# output_path.open("w", encoding="utf-8").write(img)
# displacy.render(doc, style='dep',jupyter=True)

"""Now lets apply this rule to our short sentences."""

# rule 3 function
def rule3(text):
    
    doc = nlp(text)
    
    sent = []
    
    for token in doc:

        # look for prepositions
        if token.pos_=='ADP':

            phrase = ''
            
            # if its head word is a noun
            if token.head.pos_=='NOUN':
                
                # append noun and preposition to phrase
                phrase += token.head.text
                phrase += ' '+token.text

                # check the nodes to the right of the preposition
                for right_tok in token.rights:
                    # append if it is a noun or proper noun
                    if (right_tok.pos_ in ['NOUN','PROPN']):
                        phrase += ' '+right_tok.text
                
                if len(phrase)>2:
                    sent.append(phrase)
                
    return sent

# create a df containing sentence and its output for rule 4
row_list = []

for i in range(len(df3)):
    
    sent = df3.loc[i,'Sent']
    year = df3.loc[i,'Year']
    
    # Rule 3
    output = rule3(sent)
    
    dict1 = {'Year':year,'Sent':sent,'Output':output}
    row_list.append(dict1)

df_rule3 = pd.DataFrame(row_list)
# Rule 3 achieves 40% result
output_per(df_rule3,'Output')

"""About 48% of the sentences follow this rule."""

df_rule3.head(10)

"""We can test this pattern on the entire corpus since we have good amount of sentences matching the rule."""

# create a df containing sentence and its output for rule 1
row_list = []

# df2 contains all the sentences from all the speeches
for i in range(len(df2)):
    
    sent = df2.loc[i,'Sent']
    year = df2.loc[i,'Year']
    output = rule3(sent)  # Output
    dict1 = {'Year':year,'Sent':sent,'Output':output}
    row_list.append(dict1)
    
df_rule3_all = pd.DataFrame(row_list)
# check rule1 output on complete speeches
output_per(df_rule3_all,'Output')

df_rule3_all.head(10)

"""Show only those sentences that have outputs"""

# select non-empty outputs
df_show3 = pd.DataFrame(columns=df_rule3_all.columns)

for row in range(len(df_rule3_all)):
    
    if len(df_rule3_all.loc[row,'Output'])!=0:
        df_show3 = df_show3.append(df_rule3_all.loc[row,:])

# reset the index
df_show3.reset_index(inplace=True)
df_show3.drop('index',axis=1,inplace=True)

df_rule3_all.shape, df_show3.shape

# separate noun, preposition and noun

prep_dict = dict()
dis_dict = dict()
dis_list = []

# iterating over all the sentences
for i in range(len(df_show3)):
    
    # sentence containing the output
    sentence = df_show3.loc[i,'Sent']
    # year of the sentence
    year = df_show3.loc[i,'Year']
    # output of the sentence
    output = df_show3.loc[i,'Output']
    
    # iterating over all the outputs from the sentence
    for sent in output:
        
        # separate subject, verb and object
        n1 = sent.split()[0]
        p = sent.split()[1]
        n2 = sent.split()[2:]
        
        # append to list, along with the sentence
        dis_dict = {'Sent':sentence,'Year':year,'Noun1':n1,'Preposition':p,'Noun2':n2}
        dis_list.append(dis_dict)
        
        # counting the number of sentences containing the verb
        prep = sent.split()[1]
        if prep in prep_dict:
            prep_dict[prep]+=1
        else:
            prep_dict[prep]=1

df_sep3= pd.DataFrame(dis_list)

"""The following dataframe shows the result of the rule on the entire corpus. """

df_sep3.head(10)

"""We can look at the topmost occuring prepositions in the entire corpus."""

sort = sorted(prep_dict.items(), key = lambda d:(d[1],d[0]), reverse=True)
sort[:10]

"""We look at certain prepositions to explore the sentences in detail. For example the preposition 'against'. It can give us information about what India does not support."""

# 'against'
df_sep3[df_sep3['Preposition']=='against']

"""Skimming over the nouns, some important phrases like:

* efforts against proliferation
* fight against terrorism, action against terrorism, war against terrorism
* dsicrimination against women
* war against poverty
* struggle against colonialism

... and so on. This should give us a fair idea about which sentences we want to explore in detail. For exmaple, *efforts against proliferation* talks about efforts towards nuclear disarmament. Or the sentence on *struggle against colonialism* talks about the historical links between India and Africa borne out of their common struggle against colonialism.
"""

df_sep3.loc[1272,'Sent']

df_sep3.loc[1513,'Sent']

df_sep3.loc[1618,'Sent']

df_sep3.loc[1859,'Sent']

"""As you can see, prepositions give us an important relationship between two nouns. And with a little domain knowledge we can easily seive through the vast data and determine what India supports or does not support and much more.

But at some time the output seems a bit incomplete. For example, in the sentence *efforts against proliferation*, what kind of a *proliferation* are we talking about? Certainly we need to include the modifiers attached to the nouns in the phrase, like we did in rule 2. This would definitely increase the comprehensibility of the extracted phrase.

This rule can be easily modified to include the new change. I have created a new function to extract the noun modifiers for nouns that we extracted from rule 3.
"""

# rule 0
def rule0(text, index):
    
    doc = nlp(text)
        
    token = doc[index]
    
    entity = ''
    
    for sub_tok in token.children:
        if (sub_tok.dep_ in ['compound','amod']):# and (sub_tok.pos_ in ['NOUN','PROPN']):
            entity += sub_tok.text+' '
    
    entity += token.text

    return entity

"""All we have to do is call this function whenever we encounter a noun in our phrase."""

# rule 3 function
def rule3_mod(text):
    
    doc = nlp(text)
    
    sent = []
    
    for token in doc:

        if token.pos_=='ADP':

            phrase = ''
            if token.head.pos_=='NOUN':
                
                # appended rule
                append = rule0(text, token.head.i)
                if len(append)!=0:
                    phrase += append
                else:  
                    phrase += token.head.text
                phrase += ' '+token.text

                for right_tok in token.rights:
                    if (right_tok.pos_ in ['NOUN','PROPN']):
                        
                        right_phrase = ''
                        # appended rule
                        append = rule0(text, right_tok.i)
                        if len(append)!=0:
                            right_phrase += ' '+append
                        else:
                            right_phrase += ' '+right_tok.text
                            
                        phrase += right_phrase
                
                if len(phrase)>2:
                    sent.append(phrase)
                

    return sent

# create a df containing sentence and its output for rule 3
row_list = []

# df2 contains all the sentences from all the speeches
for i in range(len(df_show3)):
    
    sent = df_show3.loc[i,'Sent']
    year = df_show3.loc[i,'Year']
    output = rule3_mod(sent)
    dict1 = {'Year':year,'Sent':sent,'Output':output}
    row_list.append(dict1)
    
df_rule3_mod = pd.DataFrame(row_list)

df_rule3_mod

"""This definitely has more information than before. For example, 'impediments in economic development' instead of 'impediments in development' and 'greater transgressor of human rights' rather than 'transgressor of rights'.

Once again combining rules has given us more power and flexibility to explore only those sentences in detail that have a meaningful extracted phrase.
"""

# separate noun, preposition and noun

prep_dict = dict()
dis_dict = dict()
dis_list = []

# iterating over all the sentences
for i in range(len(df_rule3_mod)):
    
    # sentence containing the output
    sentence = df_rule3_mod.loc[i,'Sent']
    # year of the sentence
    year = df_rule3_mod.loc[i,'Year']
    # output of the sentence
    output = df_rule3_mod.loc[i,'Output']
    
    # iterating over all the outputs from the sentence
    for sent in output:
        
        # separate subject, verb and object
        n1 = sent[0]
        p = sent[1]
        n2 = sent[2:]
        
        # append to list, along with the sentence
        dis_dict = {'Sent':sentence,'Year':year,'Noun1':n1,'Preposition':p,'Noun2':n2}
        dis_list.append(dis_dict)
        
        # counting the number of sentences containing the verb
        prep = sent[1]
        if prep in prep_dict:
            prep_dict[verb]+=1
        else:
            prep_dict[verb]=1

df_sep3_mod = pd.DataFrame(dis_list)

df_sep3

"""# End Notes

Information extraction is by no means an easy NLP task to perform. You need to spend time with the data to better understand its structure and what it has to offer.

In this article, we used theoretical knowledge and put it to practical use. We worked with a text dataset and tried to extract the information using traditional information extraction techniques.

We looked for key phrases and relationships in the text data to try and extract the information from the text. This type of approach requires a combination of computer and human effort to extract relevant information.
"""

