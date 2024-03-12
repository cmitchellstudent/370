#!/bin/env python3

'''
Letterboxd does not really have an API.
Test account:
    testfitzy1293
'''


import sys
import re

import requests
from bs4 import BeautifulSoup
from pprint import pprint
import json
from time import time
from time import sleep, time

# =======================================================================================================================================================================
# Global stuff (argparse stuff and rich console constructor).
# CL args and the console object from rich should be globals.
# Don't bother constructing console objects in every function.

import argparse

from nltk.corpus.reader import reviews

parser = argparse.ArgumentParser(description='letterboxd args')
parser.add_argument('--user', '-u', dest='user', help='letterboxd.com user')
parser.add_argument('--reviews', '-r', dest='reviews', action="store_true", default=False, help='Gets reviews')
parser.add_argument('--testing', '-t', dest='testing', action='store_true', default=False,
                    help='Testing flag - for development only')
parser.add_argument('--save-json', '-j', dest='json', action="store_true", default=False,
                    help='Saves a JSON file of the reviews dictionary')
parser.add_argument('--save-html', '-w', dest='html', action="store_true", default=False,
                    help='Saves an HTML document for easily viewing reviews')
parser.add_argument('--browser-open', '-b', dest='browserOpen', action="store_true", default=False,
                    help='Opens saved HTML document in the browser')
parser.add_argument('--search', '-s', nargs='+', dest='search', default=())
args = parser.parse_args()

from rich.console import Console
from rich import print as rprint

console = Console()
args.user = "sapphicquinn"
args.reviews = False
args.html = False
args.json = False


#How many reviews do i have?
"""
import os
directory = "C:\\Users\Connor\Desktop\letterboxd\letterboxdCorpus"
total = 0
for file in os.listdir(directory):
    if file.endswith('.json'):
        file_path = os.path.join(directory, file)
        with open(file_path, 'r') as file1:
            data = file1.readlines()
            # Counting lines in JSON file
            line_count = len(data)
            total += line_count
            total -= 5
rprint("total reviews: ", total)
"""

# =======================================================================================================================================================================

# Make a list of the pages of reviews. (Ex. /user/films/reviews/page/1 ... /user/films/reviews/page/5)
# Can use the previews of the reviews (before clicking more) to get review text for multiple movies, if the review is short enough.
# Doing it like this is faster than requesting each review individually .

def getReviewUrls(user):
    reviewsBaseUrl = f'https://letterboxd.com/{user}/films/reviews/'
    html_text = requests.get(reviewsBaseUrl).text
    soup = BeautifulSoup(html_text, 'html.parser')
    pageDiv = str(soup.find("div", {'class': "pagination"}))
    sleep(.05)
    try:
        lastValidPage = int(pageDiv.split('/films/reviews/page/')[-1].split('/')[0])
        print(lastValidPage)
        return [f'{reviewsBaseUrl}page/{str(i)}' for i in range(1, lastValidPage + 1)]

    except ValueError:

        return [reviewsBaseUrl]


def getSingleReview(url=''):
    for possibleUrl in (url, url + '/1/'):  # super-8 review had a an extra /1/ on the end
        soup = BeautifulSoup(requests.get(possibleUrl).text, 'html.parser')
        reviewDivHtmlStr = str(soup.find("div", {'class': "review body-text -prose -hero -loose"}))
        sleep(.05)
        if not reviewDivHtmlStr == 'None':
            my_string = '<p>' + reviewDivHtmlStr.split('<div><p>')[-1].replace('</div>', '')
            my_string = re.sub(r'<(\/?p|br).*?>', ' ', my_string)
            return clean(my_string)


# Should probably make different functions for batch getting all movies and searching.
# Because args.search should only be checked once, not every time there's another movie review.
# But it was too easy to just throw that in and add a continue
def clean(string):
    string = string.replace('\n', ' ').replace('\\', ' ').replace('’', '\'')
    string = string.replace('“', '\"').replace('”', '\"').replace("…", "...")
    string = string.replace('This review may contain spoilers. I can handle the truth.', ' ')
    return string
def getReviews(user):
    movieDelim = f'[red]{"=" * 80}'
    look = f'/{user}/film/'
    reviewsText = {}


    #not using search
    """
    if args.search:
        console.print(movieDelim)
        for url in [f'https://letterboxd.com/{user}/film/{movie}/' for movie in args.search]:
            movie = url.split('/film/')[-1][:-1]
            console.print(f'[cyan]movie: [bold blue]{movie}')
            console.print(f'\t[green]Searching')
            console.print(f'\t[green]Requesting: {url}')
            console.print(movieDelim)

            reviewsText[movie] = getSingleReview(url=url)
        return reviewsText
    """
    reviewUrls = getReviewUrls(user)
    console.print('[cyan] Urls with multiple reviews')
    rprint(reviewUrls)
    print()

    console.print(movieDelim)
    for url in reviewUrls:
        console.print(f'[cyan]Requesting: [bold blue]{url}')
        start = time()
        response = requests.get(url)
        rprint(f'reponseTime={time() - start}')
        console.print(movieDelim)
        htmlText = response.text

        valuableStart = htmlText.find('<ul class="poster-list -p70 film-list clear film-details-list no-title">')
        valuableEnd = htmlText.find('</section>', valuableStart)
        smallStr = htmlText[valuableStart:valuableEnd]

        #MOST OF MY CODE===============================================================================================

        titles = []
        reviews = []
        for line in smallStr.splitlines():
            soup = BeautifulSoup(line, 'html.parser')
            div_tags = soup.find_all('div')
            for div_tag in div_tags:
                title = div_tag.get('data-film-slug')
                if title is not None:
                    titles.append(title)

            ratingIndex = line.find('-green rated-')
            chopped0 = line[ratingIndex:]
            rating = ""
            if ratingIndex != -1:
                rating = chopped0[13:15] + "/10"
                rating = rating.replace("\"", "")
            reviewStart = line.find('-prose')
            if reviewStart != -1:
                chopped = line[reviewStart:]
                soup = BeautifulSoup(chopped, 'html.parser')
                paragraphs = [p.get_text() for p in soup.find_all('p')]
                paragraphs = [s + " " for s in paragraphs]
                #rprint(paragraphs)
                reviewStr = "\n".join(paragraphs)
                reviewStr = rating + " " + reviewStr
                reviews.append(clean(reviewStr))

        for i in range (len(titles)):
            #if review contains weird ...
            if "…" in reviews[i]:
                reviewsText[titles[i]] = getSingleReview(url=f'https://letterboxd.com/{user}/film/{titles[i]}/')
            #if review fits in the preview
            else:
                reviewsText[titles[i]] = reviews[i]



        """
        #doesnt run this loop for some reason
        for line in [line for line in smallStr.splitlines() if line.strip()[10:24] == '"film-detail">']:

            shorterLine = line[line.find('<p>'):]

            movieSearch = re.search(fr'{look}.*?/', shorterLine).group()
            movie = re.sub(fr'{look}', '', str(movieSearch))[:-1]


            console.print(f'[cyan]movie: [bold blue]{movie}')
            reviewPreview = shorterLine[:shorterLine.find('</div>')].strip()

            if '…' == reviewPreview[-5]:  # NOT THREE PERIODS - DIFFERENT UNICODE CHAR
                movieReviewUrl = f'https://letterboxd.com/{user}/film/{movie}/'
                console.print('\t[magenta]Preview contains partial review')
                console.print(f'\t[magenta]Requesting: {movieReviewUrl}')
                console.print(movieDelim)

                reviewsText[movie] = getSingleReview(url=movieReviewUrl)
                console.print(reviewsText)

            else:
                console.print('\t[blue]Preview contains full review')
                console.print('\t[blue]No need to request individual page')
                console.print(movieDelim)

                reviewsText[movie] = reviewPreview
                console.print(reviewsText)

            sleep(.05)
            """
    #rprint(reviewsText)
    return reviewsText


def writeReviews(reviewsDict={}):
    user = reviewsDict['user']
    if not args.search:
        fname = f'{user}_all_reviews.html'

    else:
        fname = f'{user}_searched_reviews.html'
    rprint(f'html={fname}')

    with open(fname, 'w+', encoding="utf-16") as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html>\n')
        f.write('<head>\n')
        f.write('</head>\n')
        f.write('<body>\n')

        f.write(f'<h1>{user} - letterboxd.com reviews </h1>\n<br>')

        for i, (movie, review) in enumerate(reviewsDict['reviews'].items()):
            htmlMovieTitle = movie.replace('-', ' ').title()
            f.write(f'<b>{i + 1}: {htmlMovieTitle}</b>\n<br>')
            f.write(f'{review}\n<br>')

        f.write('</body>\n')
        f.write('</html>\n')

    if args.browserOpen:
        from webbrowser import open_new_tab
        open_new_tab(fname)


def letterboxdRun():
    user = args.user
    baseUrl = f'https://letterboxd.com/{user}/films/'

    if args.reviews:
        fname = f'{user}_reviews.json'
        reviewsText = getReviews(user)
        console.print(reviewsText)
        outputDict = {'user': user, 'reviews': reviewsText}


        if args.html:
            writeReviews(outputDict)

        if args.json:
            rprint(f'json={fname}')
            jsonStr = json.dumps(outputDict, indent=3)
            with open(fname, 'w+') as f:
                f.write(jsonStr)


if __name__ == '__main__':
    console.print('[cyan]*Command line arguments* ')
    for k, v in vars(args).items():
        rprint(f'\t{k}={v}')
    print()

    console.print(
        '[cyan]--Making requests to letterboxd.com--\n[red]This may take some time depending on how many reviews there are.\n')
    letterboxdRun()
