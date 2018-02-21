import argparse
from facebook_page_crawler import FacebookPageCrawler


# Set target and parameters.
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("app_id", help="app_id of your Facebook app, the will used to access Facebook Graph API")
    parser.add_argument("app_secret", help="app_secret of your Facebook app, the will used to access Facebook Graph API")
    parser.add_argument("targets", help="Set the target fans page(at least one) you want to crawling. Ex: 'appledaily.tw' or 'appledaily.tw, ETtoday'")
    parser.add_argument("since", help="Set the start date you want to crawling. Format: 'yyyy-mm-dd HH:MM:SS'")
    parser.add_argument("until", help="Set the end date you want to crawling. Format: 'yyyy-mm-dd HH:MM:SS'")

    parser.add_argument("-att", "--attachments", action='store_true', default=False, help="Collect attachments or not, Default is False")
    parser.add_argument("-r", "--reactions", action='store_true', default=False, help="Collect reactions or not. Default is Fasle")
    parser.add_argument("-api", "--api-version", default="v2.7", help="Version of Facebook Graph API, default is v2.7")
    parser.add_argument("-l", "--limit", default=100, help="Limit of each request, larger number will decrease the number of request")
    parser.add_argument("-d", "--debug", action='store_true', default=False, help="Enable debug mode or not, Default is False")
    parser.add_argument("-p", "--process_num", help="Number process of multiprocessing, default is number of your CPU")
    parser.add_argument("-w", "--write", action='store_true', default=True, help="Write to json or not, defaut is True")

    args = parser.parse_args()

    crawler = FacebookPageCrawler(app_id=args.app_id, app_secret=args.app_secret, debug=args.debug)
    crawler.setConfig(**vars(args))
    crawler.run()

if __name__ == '__main__':
    main()
