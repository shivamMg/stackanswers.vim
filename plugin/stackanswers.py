import requests
import vim
from bs4 import BeautifulSoup

def query_google(query, domain):
    search = "https://www.google.com/search?as_q="
    url = search + query + ":" + domain
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    links = soup.findAll("li", attrs={"class": "g"})
    urls = []
    for link in links:
        url = str(link.find("h3", attrs={"class": "r"}))
        index = url.find("url")
        if index != -1:
            urls.append(url[index+6:url.find("&")])
    return urls


def get_stack_overflow_post(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    answers = soup.findAll("div", attrs={"class": "answer"})
    post = {
        "question": "",
        "answers": []
    }

    for question_header in soup.findAll("div", attrs={"id": "question-header"}):
        post["question"] = \
            question_header.find("h1", attrs={"itemprop": "name"}).getText().encode("utf-8").replace("\n", "\r")

    for answer in answers:
        content = answer.find("div", attrs={"class": "post-text"}).getText().encode("utf-8").replace("\n", "\r")
        upvotes = answer.find("span", attrs={"class": "vote-count-post"}).getText().strip()
        url = answer.find("a", attrs={"class": "short-link"})["href"].strip()
        author = answer.find("div", attrs={"class": "user-details"})
        try:
            author = author.find("a").text
        except:
            pass
        post["answers"].append([content, upvotes, url, author])
    return post


def fetch_mass_posts(query):
    urls = query_google(query, "www.stackoverflow.com")
    posts = []
    for url in urls:
        posts.append(get_stack_overflow_post(url))
    return posts

# StackAnswers output ---------------------------------------------------------


def _goto_window_for_buffer(b):
    w = int(vim.eval('bufwinnr(%d)' % int(b)))
    vim.command('%dwincmd w' % w)


def _goto_window_for_buffer_name(bn):
    b = vim.eval('bufnr("%s")' % bn)
    return _goto_window_for_buffer(b)


def _output_preview_text(lines):
    _goto_window_for_buffer_name('__Answers__')
    vim.command('setlocal modifiable')
    vim.current.buffer[:] = lines
    vim.command('silent %s/\r/\n/g')
    vim.command('silent %s/\%x00/\r/g')
    vim.command('setlocal nomodifiable')


def _generate_stack_answers_format(posts):
    response = []
    for post in posts:
        question = "Q: " + post["question"]
        response.append(question)
        response.append("%d Answer(s)\r" % len(post["answers"]))
        for answer in post["answers"]:
            response.append("=" * 80)
            response.append("www.stackoverflow.com" + answer[2] + " Upvotes: " + answer[1])
            response.append(answer[0])
    return response


def stackAnswers(query):
    query = vim.eval("a:2")
    posts = fetch_mass_posts(query)
    _output_preview_text(_generate_stack_answers_format(posts))

