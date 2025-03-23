import csv
import random

def generate_typos(domain, count=5):
    """Generates typosquatted variations of a domain."""
    typos = []
    base_domain, _, tld = domain.rpartition('.')  # Separate domain and TLD

    for _ in range(count):
        typo_method = random.choice(['swap', 'remove', 'repeat', 'replace'])
        if typo_method == 'swap' and len(base_domain) > 1:
            # Swap adjacent characters
            i = random.randint(0, len(base_domain) - 2)
            typo = base_domain[:i] + base_domain[i+1] + base_domain[i] + base_domain[i+2:]
        elif typo_method == 'remove' and len(base_domain) > 1:
            # Remove a character
            i = random.randint(0, len(base_domain) - 1)
            typo = base_domain[:i] + base_domain[i+1:]
        elif typo_method == 'repeat':
            # Repeat a character
            i = random.randint(0, len(base_domain) - 1)
            typo = base_domain[:i+1] + base_domain[i] + base_domain[i+1:]
        elif typo_method == 'replace':
            # Replace with a random character
            i = random.randint(0, len(base_domain) - 1)
            typo = base_domain[:i] + random.choice('abcdefghijklmnopqrstuvwxyz') + base_domain[i+1:]
        else:
            typo = base_domain  # Fallback in case of errors
        
        typos.append(f"{typo}.{tld}")  # Reassemble the full domain
    return typos

def append_to_csv(file_path, domains, count=5):
    """Appends typosquatted domains to an existing CSV file."""
    with open(file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for domain in domains:
            typos = generate_typos(domain, count)
            for typo in typos:
                writer.writerow([typo + ",1"])  # Append `,1` to each typosquatted domain

# List of legitimate domains with `,0` removed
domains = [
    "google.com",
    "https://youtube.com",
    "facebook.com",
    "http://twitter.com",
    "instagram.com",
    "https://wikipedia.org",
    "amazon.com",
    "http://linkedin.com",
    "microsoft.com",
    "https://apple.com",
    "netflix.com",
    "ftp://adobe.com",
    "github.com",
    "https://stackoverflow.com",
    "bing.com",
    "http://reddit.com",
    "pinterest.com",
    "https://quora.com",
    "dropbox.com",
    "ftp://wordpress.com",
    "medium.com",
    "https://slack.com",
    "zoom.us",
    "http://airbnb.com",
    "uber.com",
    "ftp://spotify.com",
    "paypal.com",
    "https://ebay.com",
    "cnn.com",
    "ftp://bbc.com",
    "nytimes.com",
    "https://forbes.com",
    "bloomberg.com",
    "http://reuters.com",
    "guardian.co.uk",
    "https://espn.com",
    "nba.com",
    "ftp://fifa.com",
    "olympics.com",
    "https://nasa.gov",
    "who.int",
    "http://un.org",
    "ted.com",
    "https://coursera.org",
    "edx.org",
    "ftp://khanacademy.org",
    "duolingo.com",
    "https://codeacademy.com",
    "udemy.com",
    "ftp://skillshare.com",
    "https://godaddy.com",
    "bluehost.com",
    "ftp://digitalocean.com",
    "aws.amazon.com",
    "http://azure.microsoft.com",
    "cloud.google.com",
    "salesforce.com",
    "ftp://zoho.com",
    "hubspot.com",
    "https://mailchimp.com",
    "stripe.com",
    "ftp://squareup.com",
    "intuit.com",
    "http://quickbooks.com",
    "turbotax.com",
    "ftp://hbr.org",
    "https://economist.com",
    "nationalgeographic.com",
    "http://discovery.com",
    "history.com",
    "ftp://imdb.com",
    "rottentomatoes.com",
    "http://metacritic.com",
    "spotifyartists.com",
    "soundcloud.com",
    "ftp://bandcamp.com",
    "http://vimeo.com",
    "dailymotion.com",
    "https://tiktok.com",
    "ftp://snapchat.com",
    "discord.com",
    "http://telegram.org",
    "signal.org",
    "ftp://protonmail.com",
    "https://duckduckgo.com",
    "brave.com",
    "http://opera.com",
    "mozilla.org",
    "chrome.google.com",
    "ftp://safari.com",
    "http://edge.microsoft.com",
    "yandex.com",
    "https://baidu.com",
    "ftp://alibaba.com",
    "http://flipkart.com",
    "myntra.com",
    "https://nykaa.com",
    "bigbasket.com",
    "ftp://zomato.com",
    "https://swiggy.com",
]

# Path to the existing CSV file
csv_file_path = r'C:\Users\HP\OneDrive\Desktop\FISHGUARD\ml\data\processed\train_urls.csv'

# Append typosquatted domains to the CSV file
append_to_csv(csv_file_path, domains)

print(f"Typosquatted domains with ',1' appended have been added to {csv_file_path}")
