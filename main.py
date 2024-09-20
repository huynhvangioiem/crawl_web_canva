import requests
import os
import shutil
import re
from bs4 import BeautifulSoup
import uuid
from urllib.parse import parse_qs, urlparse, unquote
import urllib.parse

# rnd_str = uuid.uuid4().hex
# main_name="download_" + rnd_str + "/"
main_name = "vietnam-innovation-summit-2024/"
old_href = "https://intercomeduvn.my.canva.site/vietnam-innovation-summit-2024-2"
new_href = "https://innolab.asia/vietnam-innovation-summit-2024/"

# main_name = "esg-consulting/"
# old_href = "https://vis2023.my.canva.site/esg-innolab-asia"
# new_href = "https://innolab.asia/esg-consulting/"

# main_name = "ai-transformation-advisory/"
# old_href = "https://vis2023.my.canva.site/ai-consulting-innolab-asia"
# new_href = "https://innolab.asia/ai-transformation-advisory/"

# main_name = "vietnam-innovation-summit-2023/"
# old_href = "https://vis2023.my.canva.site/vis2023"
# new_href = "https://innolab.asia/vietnam-innovation-summit-2023/"

main_folder = main_name + "/images/"
js_folder = main_name + "/js/"
font_folder = main_name + "/fonts/"
video_folder = main_name + "/videos/"

os.mkdir(main_name)
os.mkdir(main_folder)
os.mkdir(js_folder)
os.mkdir(font_folder)
os.mkdir(video_folder)
print(main_name)

response_ori = requests.get(old_href)
soup = BeautifulSoup(response_ori.text, 'html.parser')

# Regular expression pattern to match the link
pattern = r"\"/_link/\?link=(.*?)\""
# pattern = r'href="(https?://[^"]+)"'

def replace_link(match):
    print()
    print(match.group(1))
    encoded_link = match.group(1)
    decoded_link = unquote(encoded_link)
    decoded_link = decoded_link.split("&target")[0]
    decoded_link = decoded_link.split("&amp")[0]

    return f'"{decoded_link}"'

with open(main_name + "index.html", "w") as f:
    html_content = response_ori.content

    # Create a BeautifulSoup object
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the <base> element
    base_element = soup.find('base')
    # Replace the href attribute
    base_element['href'] = new_href

    # Find all <a> elements with href attribute
    link_elements = soup.find_all('a', href=True)
    # Replace old links with new links
    for link_element in link_elements:
        old_link = link_element['href']
        new_link = old_link.replace(old_href, new_href)
        link_element['href'] = new_link

    # Find all <meta> elements with content attribute
    meta_elements = soup.find_all('meta', content=True)
    # Replace href attribute in <meta> elements
    for meta_element in meta_elements:
        if meta_element.get('property') == 'og:url':
            old_href = meta_element['content']
            new_href = old_href.replace(old_href, new_href)
            meta_element['content'] = new_href

    # Find the <meta> element with the specified property attribute
    meta_element = soup.find('meta', property='og:image')
    if meta_element:
        # Replace the link in the content attribute
        thumbnail_link = meta_element['content']
        new_link = thumbnail_link.replace(old_href, new_href)
        meta_element['content'] = new_link
    else:
        thumbnail_link = None

    html_content = str(soup)

    converted_text = re.sub(pattern, replace_link, html_content)
    f.write(converted_text)

# download all images
thumbnail_link

img_tags = soup.find_all('img')
if img_tags:
    urls = [img['src'] for img in img_tags]
    for img in img_tags:
        try:
            for i in img['srcset'].split(", "):
                urls.append(i.split(" ")[0])
        except:
            pass

    if thumbnail_link:
        with open(main_name + thumbnail_link.split("/")[-1], "wb") as f:
            response = requests.get(thumbnail_link)
            f.write(response.content)

    for url in urls:
        filename = url.split("/")[1]
        with open(main_folder + filename, 'wb') as f:
            if 'http' not in url:
                url = '{}{}'.format(old_href + "/", url)
            print(url)
            response = requests.get(url)
            f.write(response.content)
else:
    print("No images found on the page.")

#find all js
for script in soup.find_all("script"):
    src = script.get("src")
    if src and src.endswith(".js"):
        print(src)
        with open(main_name + src, "wb") as f:
            response = requests.get(old_href + "/" + src)
            f.write(response.content)

# find all fonts
font_face_pattern = r'@font-face\s*{[^}]*?src:\s*url\([\'"]?(.*?\.woff2?)[\'"]?\)[^}]*}'
font_urls = re.findall(font_face_pattern, response_ori.text, re.DOTALL | re.IGNORECASE)
for font_url in font_urls:
    print(font_url)
    with open(main_name + font_url, "wb") as f:
        response = requests.get(old_href + "/" +  font_url)
        f.write(response.content)

# find all videos
vid_tags = soup.find_all('video')
for video in vid_tags:
    with open(main_name + video["src"], "wb") as f:
        response = requests.get(old_href + "/" + video["src"])
        f.write(response.content)

# find all header png
head = response_ori.text.split("<head>")[1].split("</head>")[0]
png_patterns = r'href="(.*?\.png)"'
png_urls = re.findall(png_patterns, head)

for url in png_urls:
    print(url.split("\"")[-1])
    with open(main_name + url.split("\"")[-1], "wb") as f:
        response = requests.get(old_href + "/" + url.split("\"")[-1])
        f.write(response.content)
