import os
import re
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import (
    parse_qs, urlparse, unquote, urlencode, urlunparse, urljoin
)
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Session for persistent HTTP connections
session = requests.Session()

def remove_cache_busting_param(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params.pop('v', None)
    new_query = urlencode(query_params, doseq=True)
    return urlunparse(parsed_url._replace(query=new_query))

def add_cache_busting_param(url, version):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params['v'] = version
    new_query = urlencode(query_params, doseq=True)
    return urlunparse(parsed_url._replace(query=new_query))

def replace_link(match):
    encoded_link = match.group(1)
    decoded_link = unquote(encoded_link)
    decoded_link = decoded_link.split("&target")[0]
    decoded_link = decoded_link.split("&amp")[0]
    return f'"{decoded_link}"'

def download_resource(url, local_path):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    if not url.startswith('http'):
        url = urljoin(old_href + "/", url)
    try:
        with session.get(url) as response:
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                f.write(response.content)
        logger.info(f"Downloaded: {url}")
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")

def modify_html(html_content, cache_busting_version):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Replace <base> href
    base_element = soup.find('base')
    if base_element:
        base_element['href'] = new_href

    # Replace links in <a> tags
    for link_element in soup.find_all('a', href=True):
        old_link = link_element['href']
        new_link = old_link.replace(old_href, new_href)
        link_element['href'] = new_link

    # Update meta tags
    for meta_element in soup.find_all('meta', content=True):
        if meta_element.get('property') == 'og:url' or meta_element.get('property') == 'og:image':
            old_content = meta_element['content']
            new_content = old_content.replace(old_href, new_href)
            meta_element['content'] = new_content

    # Add cache busting to resource URLs
    # For all <img> tags
    for img_tag in soup.find_all('img', src=True):
        img_tag['src'] = add_cache_busting_param(img_tag['src'], cache_busting_version)
        if 'srcset' in img_tag.attrs:
            srcset_values = img_tag['srcset'].split(",")
            new_srcset = []
            for srcset_item in srcset_values:
                parts = srcset_item.strip().split(" ")
                if len(parts) > 0:
                    parts[0] = add_cache_busting_param(parts[0], cache_busting_version)
                new_srcset.append(" ".join(parts))
            img_tag['srcset'] = ", ".join(new_srcset)

    # For all <script> tags
    for script_tag in soup.find_all('script', src=True):
        script_tag['src'] = add_cache_busting_param(script_tag['src'], cache_busting_version)

    # For all <link> tags
    for link_tag in soup.find_all('link', href=True):
        href = link_tag['href']
        # Add cache busting to CSS, fonts, and PNG files
        if 'stylesheet' in link_tag.get('rel', []) or href.endswith(('.css', '.woff', '.woff2', '.ttf', '.otf', '.png')):
            link_tag['href'] = add_cache_busting_param(href, cache_busting_version)

    # For all <video> and <source> tags
    for media_tag in soup.find_all(['video', 'source'], src=True):
        media_tag['src'] = add_cache_busting_param(media_tag['src'], cache_busting_version)

    # Handle fonts in internal <style> tags
    for style_tag in soup.find_all('style'):
        css_content = style_tag.string
        if css_content:
            # Modify font URLs in CSS
            font_url_pattern = r'url\([\'"]?(.*?)[\'"]?\)'
            def replace_font_url(match):
                font_url = match.group(1)
                # Ignore data URLs
                if not font_url.startswith('data:'):
                    font_url_with_cb = add_cache_busting_param(font_url, cache_busting_version)
                    return f"url('{font_url_with_cb}')"
                else:
                    return match.group(0)
            css_content_modified = re.sub(font_url_pattern, replace_font_url, css_content)
            style_tag.string.replace_with(css_content_modified)

    html_content = str(soup)

    # Replace encoded links
    pattern = r'"\/_link\/\?link=(.*?)"'
    converted_text = re.sub(pattern, replace_link, html_content)
    return converted_text, soup

def process_images(soup, main_name, thumbnail_link):
    img_tags = soup.find_all('img')
    urls = []
    for img in img_tags:
        src = remove_cache_busting_param(img['src'])
        urls.append(src)
        if 'srcset' in img.attrs:
            for srcset_item in img['srcset'].split(","):
                srcset_url = srcset_item.strip().split(" ")[0]
                srcset_url = remove_cache_busting_param(srcset_url)
                urls.append(srcset_url)

    if thumbnail_link:
        thumbnail_url = remove_cache_busting_param(thumbnail_link)
        filename = os.path.basename(urlparse(thumbnail_url).path)
        if filename:
            local_path = os.path.join(main_name, filename)
            download_resource(thumbnail_url, local_path)

    # Download images concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for url in urls:
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                continue
            local_path = os.path.join(main_name, 'images', filename)
            futures.append(executor.submit(download_resource, url, local_path))

        # Wait for all downloads to complete
        for future in as_completed(futures):
            pass

def process_scripts(soup, main_name):
    script_tags = soup.find_all('script', src=True)
    total_scripts = len(script_tags)
    logger.info(f"Found {total_scripts} JavaScript files to download.")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for script in script_tags:
            src = remove_cache_busting_param(script['src'])
            local_path = os.path.join(main_name, src)
            futures.append(executor.submit(download_resource, src, local_path))
        for future in as_completed(futures):
            pass
    logger.info("Completed downloading all JavaScript files.")

def process_fonts(soup, main_name):
    # From internal styles
    style_tags = soup.find_all('style')
    font_urls = set()
    font_url_pattern = r'url\([\'"]?(.*?)[\'"]?\)'
    for style_tag in style_tags:
        css_content = style_tag.string
        if css_content:
            urls = re.findall(font_url_pattern, css_content)
            for url in urls:
                if not url.startswith('data:'):
                    font_url_clean = remove_cache_busting_param(url)
                    font_urls.add(font_url_clean)

    # From CSS files
    css_links = soup.find_all('link', href=True, rel=lambda x: x and 'stylesheet' in x)
    for css_link in css_links:
        css_url = remove_cache_busting_param(css_link['href'])
        local_css_path = os.path.join(main_name, css_url)
        download_resource(css_url, local_css_path)
        # Read and modify CSS file
        try:
            with open(local_css_path, 'r') as f:
                css_content = f.read()
            css_content_modified = re.sub(
                font_url_pattern,
                lambda m: f"url('{add_cache_busting_param(m.group(1), cache_busting_version)}')"
                if not m.group(1).startswith('data:') else m.group(0),
                css_content
            )
            with open(local_css_path, 'w') as f:
                f.write(css_content_modified)
            # Extract font URLs
            urls = re.findall(font_url_pattern, css_content)
            for url in urls:
                if not url.startswith('data:'):
                    font_url_clean = remove_cache_busting_param(url)
                    font_urls.add(font_url_clean)
        except Exception as e:
            logger.error(f"Failed to process CSS {css_url}: {e}")

    # Download fonts concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for font_url in font_urls:
            filename = os.path.basename(urlparse(font_url).path)
            if not filename:
                continue
            local_path = os.path.join(main_name, font_url)
            futures.append(executor.submit(download_resource, font_url, local_path))
        for future in as_completed(futures):
            pass

def process_videos(soup, main_name):
    video_tags = soup.find_all(['video', 'source'], src=True)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for media_tag in video_tags:
            src = remove_cache_busting_param(media_tag['src'])
            filename = os.path.basename(urlparse(src).path)
            if not filename:
                continue
            local_path = os.path.join(main_name, src)
            futures.append(executor.submit(download_resource, src, local_path))
        for future in as_completed(futures):
            pass

def process_png_links(soup, main_name):
    link_tags = soup.find_all('link', href=True)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for link in link_tags:
            href = link['href']
            if href.endswith('.png'):
                url_clean = remove_cache_busting_param(href)
                filename = os.path.basename(urlparse(url_clean).path)
                if not filename:
                    continue
                local_path = os.path.join(main_name, url_clean)
                futures.append(executor.submit(download_resource, url_clean, local_path))
        for future in as_completed(futures):
            pass

if __name__ == '__main__':
    # User-defined variables
    main_name = "vietnam-innovation-summit-2024/"
    old_href = "https://intercomeduvn.my.canva.site/vietnam-innovation-summit-2024-2"
    new_href = "https://innolab.asia/vietnam-innovation-summit-2024/"

    cache_busting_version = "1.0.3"

    # Create directories
    os.makedirs(main_name, exist_ok=True)

    # Fetch and parse the webpage
    try:
        logger.info(f"Fetching the webpage: {old_href}")
        response_ori = session.get(old_href)
        response_ori.raise_for_status()
        logger.info("Webpage fetched successfully.")
    except Exception as e:
        logger.error(f"Failed to fetch {old_href}: {e}")
        exit(1)

    modified_html, soup = modify_html(response_ori.content, cache_busting_version)

    # Write modified HTML to index.html
    with open(os.path.join(main_name, "index.html"), "w", encoding='utf-8') as f:
        f.write(modified_html)
    logger.info("Modified HTML content written to index.html.")

    # Extract thumbnail link if present
    thumbnail_link = None
    meta_element = soup.find('meta', property='og:image')
    if meta_element:
        thumbnail_link = meta_element['content']

    # Process resources
    logger.info("Processing images...")
    process_images(soup, main_name, thumbnail_link)
    logger.info("Images processed.")

    logger.info("Processing JavaScript files...")
    process_scripts(soup, main_name)
    logger.info("JavaScript files processed.")

    logger.info("Processing fonts...")
    process_fonts(soup, main_name)
    logger.info("Fonts processed.")

    logger.info("Processing videos...")
    process_videos(soup, main_name)
    logger.info("Videos processed.")

    logger.info("Processing PNG links...")
    process_png_links(soup, main_name)
    logger.info("PNG links processed.")

    logger.info("All resources have been processed successfully.")
