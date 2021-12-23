from html.parser import HTMLParser


class HtmlUrlParser(HTMLParser):
    links = []
    current_url = None
    current_text = ""

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        for name, value in attrs:
            if name != "href":
                continue
            if self.current_url and self.current_text:
                self.links.append((self.current_url, self.current_text))
            if self.current_url or self.current_text:
                raise ValueError()
            self.current_url = value
            break

    def handle_endtag(self, tag):
        if tag != "a":
            return
        if self.current_url and self.current_text:
            self.links.append((self.current_url, self.current_text))

    def handle_data(self, data):
        if self.current_url:
            self.current_text += data

    def extract(self, html: str):
        self.links = []
        self.current_url = None
        self.current_text = ""
        self.feed(html)
        return self.links


class HtmlDataParser(HTMLParser):
    text = ""

    def handle_data(self, data):
        self.text += data

    def extract(self, html: str):
        self.text = ""
        self.feed(html)
        return self.text
