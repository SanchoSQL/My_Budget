import re
from urllib.request import urlopen

# Practice
"""
from urllib.request import urlopen
import re

url = "http://olympus.realpython.org/profiles/aphrodite"    # link webpage
page = urlopen(url)                                         # open webpage
html_bytes = page.read()                                    # read webpage
html = html_bytes.decode("utf-8")                           # decode webpage
print(html)                                                 # print decoded webpage

title_index = html.find("<title>")
title_index

start_index = title_index + len("<title>")
start_index

end_index = html.find("</title>")
end_index

title = html[start_index:end_index]
title
"""

url = "http://olympus.realpython.org/profiles/dionysus"             # link webpage
page = urlopen(url)                                                 # open webpage
html_text = page.read().decode("utf-8")                             # decode webpage
print(html_text)                                                    # print html

pattern = "<title.*?>.*?</title.*?>"                                # set pattern to search between titles
match_results = re.search(pattern, html_text, re.IGNORECASE)        # search with re and pass 3rd argument to ignore case
title = match_results.group()                                       # groups the search results together
print (title)                                                       # print raw title
title = re.sub("<.*?>", "", title)                                  # Remove HTML tags           
print(title)                                                        # print cleaned up title

for string in ["Name: ", "Favorite Color:"]:                        #
    string_start_idx = html_text.find(string)                       # find the string in HTML text
    text_start_idx = string_start_idx + len(string)                 #

    next_html_tag_offset = html_text[text_start_idx:].find("<")     #
    text_end_idx = text_start_idx + next_html_tag_offset            #

    raw_text = html_text[text_start_idx : text_end_idx]             #
    clean_text = raw_text.strip(" \r\n\t")                          #
    print(clean_text)                                               #

text = "Name: "
string_start_idx = html_text.find(text)                             # find the string in HTML text
print(string_start_idx)
text_start_idx = string_start_idx + len(text)                       
print(text_start_idx)
next_html_tag_offset = html_text[text_start_idx:].find("<")         #
print(next_html_tag_offset)
text_end_idx = text_start_idx + next_html_tag_offset                #
print(text_end_idx)
raw_text = html_text[text_start_idx : text_end_idx]                 #
print(raw_text)
clean_text = raw_text.strip(" \r\n\t")                              #
print(clean_text)    