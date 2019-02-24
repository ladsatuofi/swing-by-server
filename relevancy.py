import urllib.request
import json
import os.path
from bs4 import BeautifulSoup


def get_keywords() -> dict:
    # read the contents of the url
    response = urllib.request.urlopen('https://myillini.illinois.edu/Programs/MajorsCollege')
    html = response.read()
    # use BeautifulSoup to parse the html of the page with the list of majors at UIUC
    soup = BeautifulSoup(html, 'html.parser')
    majors = dict()
    # scrape the website for the majors by singling out links (HTML tag: 'a') with an HTML class = "data-description major-link"
    for link in soup.find_all('a'):
        for key in link.attrs:
            if key == 'class' and link.attrs[key] == ['data-description', 'major-link'] and link.string.find(
                    'Undeclared') == -1:
                # get links to each major to scrape keywords from the "Career Possibilities" section
                major_url = urllib.request.urlopen('https://myillini.illinois.edu' + link.get('href'))
                html = major_url.read()
                link_soup = BeautifulSoup(html, 'html.parser')
                majors[link.string] = []
                # scrape the major-specific websites to scrape keywords from the "Career Possibilities" section
                # keywords are found within the HTML div element with class = "programCareerExamples section"
                for element in link_soup.find_all('div'):
                    for label in element.attrs:
                        if label == 'class' and element.attrs[label] == ['programCareerExamples', 'section']:
                            for term in element.find_all('li'):
                                majors[link.string].append(term.string.lower())
    """Returns dict with majors as keys and a list of corresponding keywords for each major"""
    return majors


def calc_freq(text: str, topics: dict) -> dict:
    occurrences = dict()
    for subject in topics:
        freq = 0
        index = 0
        for keyword in topics[subject]:
            while text.find(keyword, index) != -1:
                index = text.find(keyword, index) + len(keyword)
                freq += 1
            occurrences[subject] = freq
    """Returns dict of occurrences of keywords for each category"""
    return occurrences


def relevant_topics(freq: list) -> list:
    # sum = 0
    max = 0
    # ratios = dict()
    subjects = []
    # find max number of occurrences
    for key in freq:
        if freq[key] > max:
            max = freq[key]
        # sum += freq[key]
    # print(sum)
    # add the subjects that have at least max * 0.3 number of occurrences to a list of subjects/categories (to remove outliers)
    for key in freq:
        if freq[key] >= max * 0.3:
            subjects.append(key)
        # ratios[key] = float(freq[key]/sum)
    # print(ratios)
    """Returns the list of subjects that are relevant to the original email text"""
    return subjects


if __name__ == '__main__':
    categories = dict()
    # if the file containing the dict for categories/keywords exists, set categories to its contents to reduce load time
    if os.path.exists("data.json"):
        with open("data.json") as f:
            categories = json.load(f)
    # otherwise, create the file by scraping the UIUC major list
    else:
        categories = get_keywords()
        with open("data.json", "w") as f:
            json.dump(categories, f)
    # add custom keywords to certain categories
    categories['Computer Science - ENG'] += ['computer science', 'machine learning', 'programming', 'icpc']
    sample_1 = '''
    Hi everyone,
    
    We hope everyone had a nice weekend. There will be an IPL meeting tonight 7 - 9 PM in Siebel 0224.  Pizza will be served at 6:45, so please come in early. The workshop will start at 7, and the topic for today is Introduction to Dynamic Programming.  There will also be a Google networking and Q&A panel this Thursday, February 21, exclusively for ICPC. Come and enjoy an informal evening with Googlers, mostly UIUC alumni, and hear about their experiences, current roles, and tips they'd have on building a successful tech career. Food and swag will be provided as well. The event would start at 6 PM in Siebel 2407. Please RSVP at bit.ly/google64QJ if you plan to attend.
    
    See you tonight!
    
    Cheers,
    ICPC Admin Team
    '''
    # convert everything in the string to be analyzed to lowercase
    sample_1 = sample_1.lower()
    frequency = calc_freq(sample_1, categories)
    tags = relevant_topics(frequency)
    print(tags)
