import aiohttp
import asyncio
from bs4 import BeautifulSoup
import zipfile
from typing import List, Dict
from openpyxl import Workbook
import os

BASE_URL = "https://www.scrapethissite.com/pages/forms/"

async def fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()

async def fetch_all_pages(base_url: str, num_pages: int) -> List[str]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_html(session, f"{base_url}?page_num={i}") for i in range(1, num_pages + 1)]
        return await asyncio.gather(*tasks)

def parse_html(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'table'})
    rows = table.find_all('tr')[1:]  # Skip header row
    data = []
    for row in rows:
        cells = row.find_all('td')
        row_data = {
            'Team Name': cells[0].text.strip(),
            'Year': cells[1].text.strip(),
            'Wins': cells[2].text.strip(),
            'Losses': cells[3].text.strip(),
            'OT Losses': cells[4].text.strip(),
            'Win %': cells[5].text.strip(),
            'Goals For (GF)': cells[6].text.strip(),
            'Goals Against (GA)': cells[7].text.strip(),
            '+ / -': cells[8].text.strip()
        }
        data.append(row_data)
    return data

async def run_etl():
    num_pages = 24  # Based on the task description
    html_pages = await fetch_all_pages(BASE_URL, num_pages)

    # Save HTML files into a Zip file
    with zipfile.ZipFile('html_files.zip', 'w') as z:
        for i, html in enumerate(html_pages, start=1):
            file_name = f"{i}.html"
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(html)
            z.write(file_name)
            os.remove(file_name)

    # Parse data from HTML pages
    all_data = []
    for html in html_pages:
        page_data = parse_html(html)
        all_data.extend(page_data)

    # Save data to Excel file
    wb = Workbook()
    
    # Sheet 1: NHL Stats 1990-2011
    ws1 = wb.active
    ws1.title = "NHL Stats 1990-2011"
    headers = ['Team Name', 'Year', 'Wins', 'Losses', 'OT Losses', 'Win %', 'Goals For (GF)', 'Goals Against (GA)', '+ / -']
    ws1.append(headers)
    for row in all_data:
        ws1.append(list(row.values()))
    
    # Sheet 2: Winner and Loser per Year
    ws2 = wb.create_sheet(title="Winner and Loser per Year")
    ws2.append(['Year', 'Winner', 'Winner Num. of Wins', 'Loser', 'Loser Num. of Wins'])
    
    data_by_year = {}
    for row in all_data:
        year = row['Year']
        if year not in data_by_year:
            data_by_year[year] = []
        data_by_year[year].append(row)

    for year, rows in data_by_year.items():
        winner = max(rows, key=lambda x: int(x['Wins']))
        loser = min(rows, key=lambda x: int(x['Wins']))
        ws2.append([year, winner['Team Name'], winner['Wins'], loser['Team Name'], loser['Wins']])
    
    wb.save('NHL_Stats.xlsx')
