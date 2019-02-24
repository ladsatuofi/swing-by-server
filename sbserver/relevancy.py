import json
import os.path
import urllib.request
from bs4 import BeautifulSoup


def get_keywords_uiuc() -> dict:
    """Returns dict with majors as keys and a list of corresponding keywords for each major"""
    response = urllib.request.urlopen('https://myillini.illinois.edu/Programs/MajorsCollege')
    soup = BeautifulSoup(response.read(), 'html.parser')
    majors = {}

    # scrape the website for the majors by singling out links
    # (HTML tag: 'a') with an HTML class = "data-description major-link"
    for link in soup.find_all('a'):
        for key in link.attrs:
            if key != 'class' or link.attrs[key] != ['data-description', 'major-link'] or \
                    link.string.find('Undeclared') != -1:
                continue
            # get links to each major to scrape keywords from the "Career Possibilities" section
            major_url = urllib.request.urlopen('https://myillini.illinois.edu' + link.get('href'))
            link_soup = BeautifulSoup(major_url.read(), 'html.parser')
            majors[link.string] = []
            # scrape the major-specific websites to scrape keywords from the "Career Possibilities" section
            # keywords are found within the HTML div element with class = "programCareerExamples section"
            for element in link_soup.find_all('div'):
                for label in element.attrs:
                    if label == 'class' and element.attrs[label] == ['programCareerExamples',
                                                                     'section']:
                        for term in element.find_all('li'):
                            majors[link.string].append(term.string.lower())
    return majors


def calc_freq(text: str, topics: dict) -> dict:
    """Returns dict of occurrences of keywords for each category"""
    text = text.lower()
    occurrences = {}
    for subject in topics:
        freq = 0
        index = 0
        for keyword in topics[subject]:
            while text.find(keyword, index) != -1:
                index = text.find(keyword, index) + len(keyword)
                freq += 1
            occurrences[subject] = freq
    return occurrences


def relevant_topics(freq: dict) -> list:
    """Returns the list of subjects that are relevant to the original email text"""
    max = 0
    subjects = []
    # find max number of occurrences
    for key in freq:
        if freq[key] > max:
            max = freq[key]
    # add the subjects that have at least max * 0.3 number of
    # occurrences to a list of subjects/categories (to remove outliers)
    for key in freq:
        if freq[key] >= max * 0.3:
            subjects.append(key)
    return subjects


def main():
    # if the file containing the dict for categories/keywords
    # exists, set categories to its contents to reduce load time
    if os.path.exists("data.json"):
        with open("data.json") as f:
            categories = json.load(f)
    else:  # otherwise, create the file by scraping the UIUC major list
        categories = get_keywords_uiuc()
        with open("data.json", "w") as f:
            json.dump(categories, f)
    # add custom keywords to certain categories
    categories['Computer Science - ENG'] += ['computer science', 'machine learning',
                                             'programming', 'icpc']
    # sample email
    sample_1 = '''
    Hi everyone,
    
    We hope everyone had a nice weekend. There will be an IPL meeting tonight 7 - 9 PM in Siebel 0224.  Pizza will be served at 6:45, so please come in early. The workshop will start at 7, and the topic for today is Introduction to Dynamic Programming.  There will also be a Google networking and Q&A panel this Thursday, February 21, exclusively for ICPC. Come and enjoy an informal evening with Googlers, mostly UIUC alumni, and hear about their experiences, current roles, and tips they'd have on building a successful tech career. Food and swag will be provided as well. The event would start at 6 PM in Siebel 2407. Please RSVP at bit.ly/google64QJ if you plan to attend.
    
    See you tonight!
    
    Cheers,
    ICPC Admin Team
    '''
    frequency = calc_freq(sample_1, categories)
    tags = relevant_topics(frequency)
    print(tags)


if __name__ == '__main__':
    main()
