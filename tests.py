from helpers import fetch_details, parse_all_details, print_articles
from loaders import save_to_csv, save_to_excel, save_to_pdf
from pubmed_sdk import PubMed

DEFAULT_QUERY = "nutrition fasting"

def main(query: str = DEFAULT_QUERY):
    parsed_articles = get_parsed_articles(query)
    print_articles(parsed_articles)
    user_input = input("Press Enter to save files, any other key to exit")
    if user_input != '':
        exit()
    save_to_pdf(parsed_articles)
    open_files()
    print("Files saved")
    return parsed_articles

def get_parsed_articles(query: str = DEFAULT_QUERY):
    wrapper = PubMed()
    results = wrapper.search(query)
    id_list = results["id_list"]
    details = fetch_details(id_list, wrapper)
    parsed_articles = parse_all_details(details)

    return parsed_articles

def open_files():
    import subprocess
    # subprocess.run(["open", "-a", "Numbers", "output.xlsx"])
    # subprocess.run(["open", "output.csv"])
    subprocess.run(["open", "output.pdf"])

if __name__ == "__main__":
    QUERY = "Severe insomnia"
    main(QUERY)
