import requests
import math
import time
import random
import json
from tqdm import tqdm


ITEMS_PER_PAGE = 100
ENDPOINT = "https://leetcode.com/graphql/"
GQL_QUERY_TEMPLATE = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
  problemsetQuestionList: questionList(
    categorySlug: $categorySlug
    limit: $limit
    skip: $skip
    filters: $filters
  ) {
    total: totalNum
    questions: data {
      acRate
      difficulty
      freqBar
      frontendQuestionId: questionFrontendId
      isFavor
      paidOnly: isPaidOnly
      status
      title
      titleSlug
      topicTags {
        name
        id
        slug
      }
      hasSolution
      hasVideoSolution
    }
  }
}
"""
HEADERS = {
    'Content-Type': 'application/json',
    'Connection': 'keep-alive',
    'Referer': 'https://leetcode.com/problemset/all/',
    'Origin': 'https://leetcode.com',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36'
}


class LeetCodeCrawler:
    def __init__(self):
        self.url = ENDPOINT
        self.query = GQL_QUERY_TEMPLATE
        self.headers = HEADERS
        self.sess = requests.Session()
        self.questions = []
        self.page = 0
        self.csrftoken = None

    def get_csrftoken(self):
        cookies = self.sess.get(self.url).cookies
        for cookie in cookies:
            if cookie.name == 'csrftoken':
                self.csrftoken = cookie.value
                self.headers['X-Csrftoken'] = cookie.value
                return

    def crawl_all(self):
        if self.csrftoken == None:
            self.get_csrftoken()
        # crawl first page & determine total questions
        res = self.crawl_page(0)
        total_questions = res['data']['problemsetQuestionList']['total']
        questions = self.parse_questions(res)
        total_pages = math.ceil(total_questions / ITEMS_PER_PAGE)
        # crawl other pages
        for i in tqdm(range(1, total_pages)):
            sleep_time = random.uniform(3, 6)
            time.sleep(sleep_time)
            res = self.crawl_page(i)
            questions += self.parse_questions(res)
        # save questions
        with open('output/questions.json', 'w') as f:
            json.dump(questions, f)

    def crawl_page(self, page: int):
        data = {
            "query": self.query,
            "variables": {
                "categorySlug": "",
                "filters": {},
                "limit": 100,
                "skip": page * ITEMS_PER_PAGE,
            },
            "operationName": "problemsetQuestionList"
        }
        res = self.sess.post(self.url, headers=self.headers, json=data)
        return res.json()

    def parse_questions(self, res):
        questions = res['data']['problemsetQuestionList']['questions']
        return questions


lc = LeetCodeCrawler()
lc.crawl_all()
