"""
Dam Removal text mining application

Input: burroughs.txt
"""
import pandas as pd
import textacy
import spacy
import requests

nlp = spacy.load('en')


# Loading related data
def get_drip_resources(URL='https://beta-gc2.datadistillery.org/api/v1/sql/bcb?q=select * from drip.dripdams'):
    """Export of known dam removals from data distillery

    Parameters
    ----------
    URL : str
        Built query for GC2.
    """
    try:
        r = requests.get(URL)
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception('Data Distillery URL returning: %s', r.status_code)
    except Exception as e:
        raise Exception(e)


def load_nlp352(file='../input/sentences_nlp352'):
    """Return a pandas dataframe from GDD export

    Notes
    -----
    Get a list of document identifiers
    >>> document_ids = pd.Series(df.docid.unique())

    Filter for an individual
    >>> df[df.docid=='5705014ccf58f18a4c0d6d61']
    """
    df = pd.read_csv(file, sep='\t', lineterminator='\n', header=None)
    df.columns = ['docid', 'sentid', 'wordidx', 'word', 'poses', 'ners', 'lemma', 'dep_paths', 'dep_parents']
    return df


def find_dam_candidate_phrases(doc_sents, keyword):
    """ Function to identify dam related phrases
    This returns a list of candidate phrase indexes
    from the document sentence list passed in.

    Parameters
    ----------
    document_sentences : list
    """
    dam_idx = []  # Return list
    
    # Iterate through the sentences looking for keyword
    for idx, sentence in enumerate(doc_sents):
        # Find occurance, append index of sentence below and above.
        # Three total sentences stored. Overlap may occur.
        if keyword in sentence.lower():
            tmp_sentence_index = []
            # print('Evaluating Sentence: ', sentence, '\n')
            tmp_sentence_index.append(doc_sents[idx])
            # Exceptions in place for first and last sentence issues.
            try:
                tmp_sentence_index.append(doc_sents[idx+1])
            except Exception:
                pass
            try:
                tmp_sentence_index.append(doc_sents[idx-1])
            except Exception:
                pass
            dam_idx.append(tmp_sentence_index)
    return dam_idx


def filter_candidate_phrases(phrases):
    """ Function to use more intensive methods to
    filter the phrases down.
    
    Parameters
    ----------
    phrases : list
        Python list of 3 sentences.
    """
    match = 0
    
    # required
    custom = [' dam', ' Dam', 'dam', 'remove', 'Remove', 'removal', 'Removal']
    match_wordlist = 0
    for sentence in phrases:
        # Clean
        phrase = sentence.replace('et', '').replace('al', '')
        for word in custom:
            if word in phrase:
                match_wordlist += 1
                print('Matched: ', word)
        if match_wordlist == 0:
            return []
        # POS
        for token in nlp(phrase):
            for dam in list(dams['name']):
                if token.text.replace(' ', '') in dam and token.pos_ == 'PROPN':
                    match += 1
    if match > 0:
        return phrases
    else:
        return []


if __name__ == '__main__':
    # Load Data Distillery dam data
    dams = pd.DataFrame([i['properties'] for i in get_drip_resources()['features']])
    # Cleaned name list
    # Rm river/dam and related words
    dams['name'] = dams['dam_name'].str.replace('Dam', '').replace('River', '').replace('River)', '').replace('dam', '')

    # Sample document from PDFtoText
    with open('./data/burroughs.txt', 'r') as f:
        file = f.read()
    doc = textacy.preprocess_text(file, fix_unicode=True).replace('\n', ' ')

    # Example processing
    doc_sents = doc.split('.')  # Separate by sentences
    print('Sentences: %s' % len(doc_sents))
    candidate_phrases = find_dam_candidate_phrases(doc_sents[:], ' dam')
    print('Candidate sentences: %s' % (len(candidate_phrases)))

    # Working sample
    test = '. '.join(candidate_phrases[3])
    # Fail sample
    fail = ['There is not the phrase.', 'hi 2345', 'What is a bad sentence?']
    # Test workflow
    # print(filter_candidate_phrases(fail))

    # Full run on doc
    for i in candidate_phrases:
        print(filter_candidate_phrases(i))
        print('====================================')
