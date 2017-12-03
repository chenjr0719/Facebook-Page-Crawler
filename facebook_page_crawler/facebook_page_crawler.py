import os
import json
import requests
from datetime import datetime
from uuid import uuid4
from multiprocessing import Pool, cpu_count
from .logger import logger


class FacebookPageCrawler:

    __slots__ = (
        'id', 'result_dir', 'token', 'session', 'api_endpoint',
        'api_version', 'targets', 'since', 'until', 'limit',
        'process_num', 'write', 'fields', 'attachments', 'reactions',
        'debug', 'requests', 'target_dir'
    )

    def __init__(self, app_id=None, app_secret=None, debug=False):

        if not app_id or not app_secret:
            logger.error('app_id or app_secret is None, Please provide your app_id and app_secret')
            raise Exception('app_id or app_secret is None, Please provide your app_id and app_secret')

        self.token = app_id + '|' + app_secret
        self.session = requests.Session()
        self.api_endpoint = 'https://graph.facebook.com'
        self.debug = debug
        self.requests = []

        logger.info('Initialize crawler')

        if self.debug:
            logger.setLevel('DEBUG')
            logger.debug('Initialize with debug mode')

    def setConfig(self, **kwargs):
        self.targets = kwargs.get('targets', None)
        self.since = kwargs.get('since', None)
        self.until = kwargs.get('until', None)

        if not self.targets or not self.since or not self.until:
            logger.error('Please set targets, since and until correctly')
            raise Exception('Please set targets, since and until correctly')

        if ',' in self.targets:
            self.targets = self.targets.split(',')

        self.since = int(
            datetime.strptime(
                self.since,
                '%Y-%m-%d %H:%M:%S'
            ).timestamp()
        )
        self.until = int(
            datetime.strptime(
                self.until,
                '%Y-%m-%d %H:%M:%S'
            ).timestamp()
        )

        self.api_version = kwargs.get('api_version', 'v2.7')
        if not self.api_version.startswith('v'):
            self.api_version = 'v' + self.api_version
        self.limit = kwargs.get('limit', 100)

        self.process_num = kwargs.get('process_num', cpu_count())
        self.write = kwargs.get('write', True)

        self.fields = kwargs.get(
            'fields',
            {
                'id': True,
                'message': True,
                'description': True,
                'comments': {
                    'id': True,
                    'message': True,
                    'from': True,
                    'like_count': True
                },
                'likes': True
            }
        )

        self.attachments = kwargs.get('attachments', False)
        if self.attachments:
            self.fields.update({
                'attachments': {
                    'url': True,
                    'description': True
                }
            })
            self.fields['comments'].update({
                'attachments': True
            })

        self.reactions = kwargs.get('reactions', False)
        if self.reactions:
            self.fields.update({
                'reactions': {
                    'id': True,
                    'username': True,
                    'type': True
                }
            })

        params = {
            'access_token': self.token
        }

        targets_info_url = '/'.join([
            self.api_endpoint,
            self.api_version,
            self.targets
        ])

        targets_info = self.session.get(
            targets_info_url,
            params=params
        )
        logger.info('GET from %s', targets_info_url)
        logger.debug({'headers': targets_info.request.headers, 'body': targets_info.request.body, 'url': targets_info.request.url})

        if self.debug:
            self.requests.append(targets_info.request)

        if targets_info.ok:
            return targets_info.json()
        else:
            error = targets_info.json()['error']
            logger.error('GET node %s error: %s - %s', self.targets, error['type'], error['message'])
            return error['message']

    @property
    def config(self):
        config = {
            'targets': self.targets,
            'since': self.since,
            'until': self.until,
            'fields': self.fields,
            'api_version': self.api_version,
            'limit': self.limit,
            'process_num': self.process_num,
            'write': self.write
        }

        return config

    def _field_parser(self, fields):
        parsed_fields = []
        for key, value in fields.items():
            if value is True:
                parsed_fields.append(key)
            elif isinstance(value, dict):
                parsed_fields.append(key + '{' + ','.join(self._field_parser(value)) + '}')
        return parsed_fields

    @property
    def parsed_fields(self):
        return self._field_parser(self.fields)

    def fetchFeeds(self, target=None, feeds_url=None):

        params = {
            'limit': self.limit,
            'since': self.since,
            'until': self.until,
            'access_token': self.token,
            'fields': ','.join(self.parsed_fields)
        }

        if target:
            feeds_url = '/'.join([
                self.api_endpoint,
                self.api_version,
                target,
                'feed'
            ])

            feeds = self.session.get(
                feeds_url,
                params=params
            )
        elif feeds_url:
            feeds = self.session.get(
                feeds_url
            )

        if not feeds.ok:
            raise Exception('Fetch feeds failed')

        if self.debug:
            self.requests.append(feeds.request)

        feeds = feeds.json()

        if feeds.get('paging', {}).get('next', None):
            next = self.fetchFeeds(feeds_url=feeds['paging']['next'])
            feeds['data'].extend(next)

        if feeds['data'] and len(feeds['data']) > 0:
            return feeds['data']
        else:
            return []

    def fetchSubField(self, field=None, next_url=None):

        if next_url:
            field = self.session.get(
                next_url
            )

            if not field.ok:
                raise Exception('Fetch sub-field failed')

            if self.debug:
                self.requests.append(field.request)

            field = field.json()

        if isinstance(field, dict):
            if field.get('paging', {}).get('next', None):
                next = self.fetchSubField(next_url=field['paging']['next'])
                field['data'].extend(next)

            if field['data'] and len(field['data']) > 0:
                return field['data']
            else:
                return []

        else:
            return field

    def fetchFeedAllFields(self, feed):
        for key, field in feed.items():
            if key != 'id':
                logger.info('Fetch sub-field: %s of feed: %s', key, feed['id'])
                feed[key] = self.fetchSubField(field=field)

        if self.write:
            feed_dir = os.path.join(self.target_dir, feed['id'])
            os.makedirs(feed_dir, exist_ok=True)

            feed_path = os.path.join(feed_dir, feed['id']) + '.json'
            with open(feed_path, 'w') as f:
                feed_content = {}
                if 'description' in feed:
                    feed_content.update({'description': feed['description']})
                if 'message' in feed:
                    feed_content.update({'message': feed['message']})
                f.write(json.dumps(feed_content, indent=4))

            for key, field in feed.items():
                write_fields = ['comments', 'likes', 'reactions']
                if key in write_fields:
                    field_dir = os.path.join(feed_dir, key)
                    os.makedirs(field_dir, exist_ok=True)

                    for item in field:
                        item_path = os.path.join(field_dir, item['id']) + '.json'
                        with open(item_path, 'w') as f:
                            f.write(json.dumps(item, indent=4))

        return feed

    def run(self):

        self.id = str(uuid4())

        if self.write:
            self.result_dir = os.path.join('Results/', self.id)
            os.makedirs(self.result_dir, exist_ok=True)

        start_time = datetime.now()

        logger.info('Run crawler, task id: %s with config: %s', self.id, self.config)
        logger.info('Run crawler at %s', datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S'))

        if not isinstance(self.targets, list):
            self.targets = [self.targets]

        target_feeds = {target: self.fetchFeeds(target) for target in self.targets}

        for target, feeds in target_feeds.items():
            if self.write:
                self.target_dir = os.path.join(self.result_dir, target)
                os.makedirs(self.target_dir, exist_ok=True)

            logger.info('Fetch sub-fields of target: %s', target)
            pool = Pool(self.process_num)
            feeds = pool.map(self.fetchFeedAllFields, feeds)
            pool.close()
            pool.terminate()

            target_feeds[target] = feeds

        if self.target_dir:
            del self.target_dir

        finsh_time = datetime.now()
        logger.info('Finsh crawling at %s', datetime.strftime(finsh_time, '%Y-%m-%d %H:%M:%S'))
        logger.info('Excution time: %s', str(finsh_time - start_time))

        return target_feeds
