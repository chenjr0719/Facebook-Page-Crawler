# Facebook-Page-Crawler

A Python crawler uses Facebook Graph API to crawling fan page's public posts, comments, and reactions.

## How does it work?

Using **Facebook Graph API**, that's all.

## Requirement

**Facebook Page Crawler** is built by **Python 3** and use **requests** module.

Please make sure that you have already install **requests**.

If not, you can use **pip** to install:
```
pip install requests
```

## How to use?

**Facebook Page Crawler** require at least **three** parameters:

1. **target**: The page name you want to crawl.
2. **since**: The date you want to start the crawling.
3. **until**: The date you want to finish the crawling.

And **two** additional parameters:

1. **-r, --reactions**: Default is **no**. Set to **yes** will collect reactions data. Because the number of reactions is too large, use it **CAREFULLY!!!**
2. **-s, --stream**: Default is **no**. Set to **yes** will turn to streaming mode.

You can use this two command to find some help:
```
python Facebook_Page_Crawler.py -h
python Facebook_Page_Crawler.py --help
```

### Example usage

```
python Facebook_Page_Crawler.py 'appledaily.tw' '2016-09-01 00:00:00' '2016-09-01 23:59:59'
python Facebook_Page_Crawler.py 'appledaily.tw' '2016-09-01 00:00:00' '2016-09-01 23:59:59' -r yes
python Facebook_Page_Crawler.py 'appledaily.tw' '2016-09-01 00:00:00' '2016-09-01 23:59:59' -s yes
python Facebook_Page_Crawler.py 'appledaily.tw' '2016-09-01 00:00:00' '2016-09-01 23:59:59' -r yes -s yes
python Facebook_Page_Crawler.py 'appledaily.tw,ETtoday' '2016-09-01 00:00:00' '2016-09-01 23:59:59'
```

## About token

This crawler use **app_id**, **app_secret** to get the token.

Replace **app_id**, **app_secret** to use your own app setting.

## Multi-Processing

This crawler add **multi-processing** now, it will parallel processing feeds at the same time.

By default, it will use the number of your CPU to create process.

You can also modifiy it, but do not use too large number.
