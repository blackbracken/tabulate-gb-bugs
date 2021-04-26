from typing import Optional

from github import Github
from github.Issue import Issue

from time import sleep
from random import randint
from logging import getLogger, FileHandler, Formatter, DEBUG
import csv
import datetime
import sys

from translator import japanize

DATE_RELEASED_4_0 = datetime.datetime(2016, 4, 30)
RETRY_LIMIT = 5
TITLE_BREAK_LENGTH = 12

logger = getLogger(__name__)
logger.setLevel(DEBUG)
handler = FileHandler(filename=f"{datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.log")
handler.setLevel(DEBUG)
formatter = Formatter("%(asctime)s | [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False


def main():
    if len(sys.argv) != 2:
        print('GITHUB_API_TOKEN must be exist as command line argument')
        return

    gh = Github(sys.argv[1])
    repo = gh.get_repo("gitbucket/gitbucket")

    issues = repo.get_issues(
        labels=["bug"], state="closed", sort="created", since=DATE_RELEASED_4_0
    )

    with open("bugs.csv", 'w', newline="", encoding="utf_8_sig") as f:
        w = csv.writer(f)

        write_header(w)

        for issue in issues:
            issue_num = str(issue.number)

            if write_issue(w, issue):
                logger.info(f"wrote #{issue_num}")
            else:
                logger.info(f"missed #{issue_num}")


def write_header(writer):
    writer.writerow([
        "ナンバー",
        "タイトル",
        "内容",
        "報告されたバージョン",
        "URL"
    ])


def write_issue(writer, issue: Issue) -> bool:
    for _ in range(RETRY_LIMIT):
        try:
            if issue.pull_request is not None:
                return False

            row = gen_issue_row(issue)
            writer.writerow(row)
            return True
        except Exception:
            sleep(randint(5, 10))
            continue

    logger.warn(f"failed to write #{str(issue.number)}")
    return False


def gen_issue_row(issue: Issue) -> [str]:
    title = break_long_text(japanize(issue.title))
    body = japanize(omit_snippets(issue.body))

    return [
        str(issue.number),
        title,
        body,
        issue.milestone.title if issue.milestone is not None else "マイルストーンなし",
        issue.url
    ]


def break_long_text(text: str) -> str:
    return '\n'.join([text[i:i + TITLE_BREAK_LENGTH] for i in range(0, len(text), TITLE_BREAK_LENGTH)])


def omit_snippets(text: str) -> str:
    while True:
        tail = len(text) - 1
        left = text.find("```")
        if left == -1:
            break
        right = text.find("```", left + 3)
        if right == -1:
            right = tail

        text = text[:left - 2] + "\n[OMITTED_SNIPPET]" + text[right + 3:]

        if right == tail:
            break

    return text


if __name__ == '__main__':
    main()
