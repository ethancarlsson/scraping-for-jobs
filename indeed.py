import requests
from bs4 import BeautifulSoup as bs
import csv
import datetime
import io


def main(url, pages, search):
    all_pages = [url]
    page_index = 10

    for _ in range(pages):
        next_page = url + f'&start={page_index}'
        all_pages.append(next_page)
        page_index+=10
    
    all_job_links = []

    for page in all_pages:
        page_url = requests.get(page)
        soup = bs(page_url.text, 'lxml')
        
        jobs = soup.find_all('h2', class_="title")
        
        for job in jobs:
            tilelink = job.find('a', class_="jobtitle turnstileLink")
            href = tilelink.get('href')
            all_job_links.append(href)
    
    today = datetime.datetime.now()
    time = today.strftime('%d%b%H%p')    

    page_urls = []
    job_titles = []
    descriptions = []
    company_links = []

    for link in all_job_links:
        clean_link = link.replace('/rc/clk?', '')
        
        job_url = 'https://es.indeed.com/ver-oferta?' + clean_link
        page_urls.append(job_url)

        page_url = requests.get(job_url)
        soup = bs(page_url.text, 'lxml')

        job_title = soup.find('h1', class_='icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title')
        try:
            job_titles.append(job_title.text)
        except AttributeError:
            job_titles.append(job_title)
        
        description = soup.find('div', class_='jobsearch-jobDescriptionText')
        try:
            descriptions.append(description.text)
        except AttributeError:
            descriptions.append(description)
        solicitar_en_la_pagina = soup.find('a', class_="icl-Button icl-Button--primary icl-Button--block")
        try:
            company_link = solicitar_en_la_pagina.get('href')
            company_links.append(company_link)
        except AttributeError:
            company_link = 'No link found'
            company_links.append(company_link)

    transposer = [page_urls, job_titles, descriptions, company_links]
    transposed_list = list(map(list, zip(*transposer)))

    all_jobs = []
    new_jobs = []

    try:
        with io.open(f'all_jobs_so_far{search}.csv', 'r') as all_jobs_so_far:
            for line in csv.reader(all_jobs_so_far):
                all_jobs.append(tuple(line))

    except FileNotFoundError:
        print('file not found')
        with io.open(f'all_jobs_so_far{search}.csv', 'w', newline='') as all_jobs_so_far:
            job_writer = csv.writer(all_jobs_so_far)
            for row in transposed_list:
                job_writer.writerow(row)

    for line in transposed_list:
        new_jobs.append(tuple(line))
    
    set1 = set(all_jobs)
    set2 = set(new_jobs)
    only_new_jobs = set2 - set1

    update_all_jobs = list(set1.union(only_new_jobs))
    with io.open(f'all_jobs_so_far{search}.csv', 'w', newline='') as all_jobs_so_far:
        job_writer = csv.writer(all_jobs_so_far)
        for row in update_all_jobs:
            try:
                job_writer.writerow(row)
            except UnicodeEncodeError:
                print('unicode error')
                pass

    with io.open(f'new_jobs_{search}_{time}.csv', 'w', newline='') as new_jobs:
        job_writer = csv.writer(new_jobs)
        for row in transposed_list:
            try:
                job_writer.writerow(row)
            except UnicodeEncodeError:
                print('unicode error')
                pass



if __name__ == "__main__": 
    main(str(input('URL: ')), int(input('number of pages: ')), str(input('search term: ')))
