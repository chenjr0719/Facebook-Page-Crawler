# Facebook-Page-Crawler

A Python crawler uses Facebook Graph API to crawling fan page's public posts, comments, and reactions.

## How does it work?

Using **Facebook Graph API**, that's all.

## Installation

**Facebook Page Crawler** is built on **Python 3** and use **requests** module.
After clone this repository, use following command to install this module:
```
python setup.py develop
```

This crawler can be used under command line as:
```
facebook_page_crawler $app_id $app_secret $targets $since $until
```

## Uninstallation

Run following command:
```
python setup.py develop --uninstall
```

## How to use?

**Facebook Page Crawler** requires **five** arguments:

1. **app_id**: app_id of your Facebook app, the will used to access Facebook Graph API.
2. **app_secret**: app_secret of your Facebook app, the will used to access Facebook Graph API.
3. **targets**: The page name you want to crawl.
4. **since**: The date you want to start the crawling.
5. **until**: The date you want to finish the crawling.

And other additional arguments:

1. **-att, --attachments**: Default is **False**. Set to **True** will collect attachments of post and comments.
2. **-r, --reactions**: Default is **False**. Set to **True** will collect reactions data. Because the number of reactions is too large, use it **CAREFULLY!!!**
3. **-api, --api-version**: Default is **v2.7**. This will cange the version of **Facebook Graph API**, but currently this crawler only test under **v2.7**.
4. **-l, --limit**: Default is **100**. This argument will limit the number of feed or comments of each request, larger number will decrease the number of request.
5. **-d, --debug**: Default is **False**. Enable debug mode to see additional information of crawling.
6. **-p, --process_num**: Default is the number of your CPU. Parallel processing feeds at the same time.
7. **-w, --write**: Default is **True**. Write to json files under `Results/`

You can use this command to find some help:
```
facebook_page_crawler --help
```

### Example usage

```
facebook_page_crawler $APP_ID $APP_SECRET 'appledaily.tw' '2016-09-01 00:00:00' '2016-09-01 23:59:59'
facebook_page_crawler $APP_ID $APP_SECRET 'appledaily.tw' '2016-09-01 00:00:00' '2016-09-01 23:59:59' -r yes
facebook_page_crawler $APP_ID $APP_SECRET 'appledaily.tw,ETtoday' '2016-09-01 00:00:00' '2016-09-01 23:59:59'
```

## About token

This crawler use **app_id**, **app_secret** to get the token.

Please create an app at https://developers.facebook.com/ and use the **app_id** and **app_secret** at this crawler.

## TODO

1. Add tests
2. Maybe publish to PyPI
3. Counts of reactions and likes
