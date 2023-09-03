from bs4 import BeautifulSoup


def parse_html(file_name):
    with open(file_name, 'r', encoding='utf-16-le') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'html.parser')
    trs = soup.find_all('tr')
    deal_found = False
    deal_rows = []
    headers = []

    for tr in trs:
        if tr.get('bgcolor') == '#FFFFFF' and deal_found:
            deal_rows.append(tr)

        th = tr.find('th')
        if th and th.text.strip() == 'Сделки':
            deal_found = True
            headers = [th.text.strip() for th in tr.find_next('tr').find_all('td')]

    # Create a list of dictionaries, each representing one deal
    deals = []
    for tr in deal_rows:
        deal = {}
        for header, td in zip(headers, tr.find_all('td')):
            deal[header] = td.text.strip()
        deals.append(deal)

    return deals
