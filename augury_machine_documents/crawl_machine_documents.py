import requests
import os
import getpass
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
import json

def tavily_crawl(
    url: str,
    max_depth: int = 1,
    max_breadth: int = 20,
    include_images: bool = False,
    limit: int = 50,
    select_paths: list[str] = None,
    select_domains: list[str] = None,
    allow_external: bool = False,
    categories: list[str] = None,
    extract_depth: str = "basic"
):
    """
    Crawl a website using Tavily's Crawl API.
    
    Args:
        url: The root URL to begin the crawl.
        max_depth: Max depth of the crawl tree. Defines how far from the base URL the crawler can explore.
        max_breadth: Max number of links to follow per level of the tree (i.e., per page).
        limit: Total number of links the crawler will process before stopping.
        select_paths: Regex patterns to select only URLs with specific path patterns.
        select_domains: Regex patterns to select crawling to specific domains or subdomains.
        allow_external: Whether to allow following links that go to external domains.
        categories: Filter URLs using predefined categories like documentation, blog, api, etc.
        extract_depth: Advanced extraction retrieves more data. Options: "basic" or "advanced".
    
    Returns:
        The API response from Tavily.
    """
    payload = {
        "url": url,
        "max_depth": max_depth,
        "max_breadth": max_breadth,
        "limit": limit,
        "include_images": include_images,
        "extract_depth": extract_depth
    }
    
    # Add optional parameters only if they're provided
    if select_paths:
        payload["select_paths"] = select_paths
    
    if select_domains:
        payload["select_domains"] = select_domains
    
    if allow_external:
        payload["allow_external"] = allow_external
    
    if categories:
        payload["categories"] = categories

    crawl_result = requests.post(
        "https://api.tavily.com/crawl",
        headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
        json=payload
    )
    
    return crawl_result

# Example usage
if __name__ == "__main__":
    # base_url = "https://www.rossi.com/en/Products/Industrial-Gear-Units/G-Series/"
    base_url = "https://www.baldor.com/catalog#category=69"
    response = tavily_crawl(
        url=base_url, 
        max_depth=5, 
        max_breadth=100,
        include_images=False,
        select_paths=[".*pdf"],
        categories=['Media'], 
        extract_depth="advanced")
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print(response.json())
        exit()
    # create a directory to save the files
    dir_name = base_url.replace("https://www.", "").replace("/", "_").split(".")[0]
    path_dir = os.path.join(os.path.dirname(__file__), dir_name)
    os.makedirs(path_dir, exist_ok=True)
    # save response to file relative to this file
    file_path = os.path.join(path_dir, "crawl_result.json")
    with open(file_path, "w") as f:
        json.dump(response.json(), f, indent=4)

    # save metadata to file relative to this file
    file_path = os.path.join(path_dir, "crawl_metadata.json")
    with open(file_path, "w") as f:
        json.dump(response.json()["metadata"], f, indent=4)

    for document in response.json()["data"]:
        file_name = document["url"].split("/")[-1].split(".")[0]
        with open(os.path.join(path_dir, f"{file_name}.txt"), "w") as f:
            f.write(document["raw_content"])
        # if it's a pdf, save as pdf
        if document["url"].endswith(".pdf"):
            with open(os.path.join(path_dir, f"{file_name}.pdf"), "wb") as f:
                # download the pdf
                response = requests.get(document["url"])
                f.write(response.content)
