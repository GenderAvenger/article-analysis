import requests, mediacloud.api

def article_urls(start, rows, id):
    start = 0
    rows  = 1000
    while True:
        params = {
            'last_processed_stories_id': start,
            'rows': rows,
            'q': 'media_id:' + str(id),
            'fq': 'publish_date:[2020-06-21T09:00:00Z TO 2020-06-22T09:00:00Z]',
            'key': '56db1b3371386348692be15924705bf1c3530d7ef82c97e327073768d88f6aa1'
        }

        #print("Fetching {} stories starting from {}").format( rows, start)
        r = requests.get( 'https://api.mediacloud.org/api/v2/stories_public/list/', params = params, headers = { 'Accept': 'application/json'} )
        stories = r.json()

        if len(stories) == 0:
            break

        urls =[]
        start = stories[ -1 ][ 'processed_stories_id' ]
        for d in stories:
            urls.append(d['url'])
    return urls
