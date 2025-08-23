"""
Simplified crawler API without external dependencies
This is a simplified version that works without scraping for demo purposes
"""
import threading
import hashlib
import random
import datetime

from newsapp.models import NewsArticle, NewsSource

# Sample headlines and summaries for demo purposes with common keywords like politics, sports, technology, business, entertainment
SAMPLE_NEWS = [
    {
        "headline": "Government Announces New Economic Package for Business Growth",
        "summary": "The government has unveiled a new economic stimulus package aimed at boosting business growth and creating jobs. Politics and economics experts weigh in on the impact."
    },
    {
        "headline": "Scientists Discover New Technology in Amazon Rainforest Research",
        "summary": "Researchers have identified five previously unknown species using advanced technology during an expedition to the Amazon rainforest."
    },
    {
        "headline": "Tech Company Launches Revolutionary AI Assistant for Business",
        "summary": "A leading technology firm has introduced an AI assistant that promises to transform how businesses interact with technology."
    },
    {
        "headline": "Sports: National Cricket Team Wins International Tournament",
        "summary": "In a thrilling final match, the national cricket team secured victory in the international sports tournament."
    },
    {
        "headline": "Entertainment: Film Festival Announces Award Winners",
        "summary": "The annual film festival wrapped up yesterday with the announcement of this year's entertainment award-winning movies and performances."
    },
    {
        "headline": "Health Politics: Ministry Issues New Dietary Guidelines",
        "summary": "The Ministry of Health has released updated dietary guidelines emphasizing plant-based foods and reduced sugar intake. Political debate continues about implementation."
    },
    {
        "headline": "Business: Stock Market Reaches Record High with Technology Stocks",
        "summary": "The business stock market closed at an all-time high yesterday, driven by strong technology company earnings reports and positive economic data."
    },
    {
        "headline": "University Researchers Develop New Renewable Energy Technology",
        "summary": "A team of scientists has created a more efficient technology for solar panels that could significantly reduce business costs."
    },
    {
        "headline": "Entertainment: Famous Author Announces New Book Series on Politics",
        "summary": "The bestselling entertainment author revealed plans for a new trilogy that will explore politics and social issues in a fantasy setting."
    },
    {
        "headline": "Weather Department Predicts Above Average Monsoon Impact on Sports",
        "summary": "Meteorologists forecast an above-average monsoon season this year, bringing relief to drought-affected regions and impacting outdoor sports events."
    },
    {
        "headline": "Politics: Prime Minister Addresses Nation on Economic Reforms",
        "summary": "The Prime Minister delivered a televised speech outlining new politics and economic policies aimed at accelerating growth and reducing inflation."
    },
    {
        "headline": "Cricket: National Team Announces New Captain for World Cup",
        "summary": "The cricket board has named a new captain to lead the national sports team in the upcoming World Cup tournament."
    },
    {
        "headline": "Technology Giant Unveils New Smartphone with AI Features",
        "summary": "The leading technology company launched its latest smartphone model featuring advanced AI capabilities and improved camera technology."
    },
    {
        "headline": "Business Leaders Conference Discusses Future of Work",
        "summary": "CEOs and business experts gathered to discuss how technology and automation will reshape employment in the next decade."
    },
    {
        "headline": "Entertainment Industry Report Shows Growth in Streaming Services",
        "summary": "A new entertainment industry analysis reveals significant growth in streaming platforms and declining traditional media consumption."
    }
]

# Keyword-specific article templates
KEYWORD_TEMPLATES = {
    "cricket": [
        {
            "headline": "Cricket: India Defeats Australia in Thrilling Test Match",
            "summary": "The Indian cricket team secured a dramatic victory against Australia in the final day of the Test match, with exceptional performances from its batsmen and bowlers."
        },
        {
            "headline": "IPL Auction: Records Broken as Teams Bid for Top Cricket Talent",
            "summary": "The Indian Premier League auction saw unprecedented spending as cricket franchises competed to secure the best players for the upcoming season."
        },
        {
            "headline": "Cricket Star Announces Retirement After 15-Year Career",
            "summary": "One of cricket's most celebrated players has announced their retirement from international cricket after a stellar career spanning 15 years and numerous accolades."
        },
        {
            "headline": "Cricket World Cup Schedule Announced for Next Year",
            "summary": "The International Cricket Council has released the complete schedule for next year's Cricket World Cup, with matches to be held across multiple countries."
        },
        {
            "headline": "New Cricket Stadium Inaugurated in Mumbai",
            "summary": "A state-of-the-art cricket stadium has been opened in Mumbai, featuring advanced facilities and a capacity of over 75,000 spectators for international cricket matches."
        }
    ],
    "politics": [
        {
            "headline": "Election Results: Ruling Party Maintains Majority in Parliament",
            "summary": "The ruling political party has secured another term in office following yesterday's general election, though with a reduced majority according to politics analysts."
        },
        {
            "headline": "Opposition Leader Calls for Political Reforms in Fiery Speech",
            "summary": "The leader of the opposition delivered a powerful address criticizing the current administration and calling for substantial political reforms."
        },
        {
            "headline": "New Political Coalition Forms Ahead of Regional Elections",
            "summary": "Several political parties have announced the formation of a coalition to contest the upcoming regional elections, potentially reshaping the political landscape."
        },
        {
            "headline": "Parliament Passes Controversial Political Reform Bill",
            "summary": "After heated debate, lawmakers approved a major political reform bill that will significantly change electoral procedures in future elections."
        },
        {
            "headline": "Political Tensions Rise as Trade Negotiations Stall",
            "summary": "Diplomatic relations have become strained as international trade negotiations between political leaders reached an impasse over key economic provisions."
        }
    ],
    "technology": [
        {
            "headline": "Revolutionary AI Technology Transforms Medical Diagnosis",
            "summary": "A new artificial intelligence system has demonstrated remarkable accuracy in diagnosing medical conditions, potentially transforming healthcare technology."
        },
        {
            "headline": "Technology Giant Opens New R&D Center Focused on Quantum Computing",
            "summary": "A leading technology company has invested billions in a new research facility dedicated to advancing quantum computing technology and applications."
        },
        {
            "headline": "Breakthrough in Battery Technology Promises Longer-Lasting Devices",
            "summary": "Scientists have developed a new battery technology that could double the life of smartphones and electric vehicles while reducing charging time."
        },
        {
            "headline": "Technology Conference Showcases Next-Generation Virtual Reality",
            "summary": "The annual technology expo featured impressive demonstrations of upcoming virtual reality systems that promise more immersive experiences than ever before."
        },
        {
            "headline": "Government Announces Major Investment in Technology Education",
            "summary": "The administration has unveiled a comprehensive plan to enhance technology education in schools and universities to prepare students for the digital economy."
        }
    ],
    "business": [
        {
            "headline": "Major Business Merger Creates New Industry Leader",
            "summary": "Two business giants have finalized a merger agreement creating one of the largest companies in the sector, subject to regulatory approval."
        },
        {
            "headline": "Start-up Secures Record Business Funding for Expansion",
            "summary": "A promising start-up has received unprecedented investment from venture capitalists to expand its business operations globally."
        },
        {
            "headline": "Business Confidence Index Shows Strong Economic Outlook",
            "summary": "The latest business confidence survey indicates optimism among executives regarding economic growth and market opportunities in the coming year."
        },
        {
            "headline": "New Business Regulations to Impact Financial Sector",
            "summary": "Regulatory authorities have announced new compliance requirements that will significantly affect how businesses in the financial industry operate."
        },
        {
            "headline": "International Business Forum Addresses Sustainability Challenges",
            "summary": "Leaders from major businesses worldwide gathered to discuss strategies for implementing sustainable practices while maintaining profitability."
        }
    ],
    "sports": [
        {
            "headline": "Olympic Committee Announces Host City for 2036 Games",
            "summary": "The International Olympic Committee has selected the city that will host the 2036 Summer Olympics following an extensive evaluation of competing bids."
        },
        {
            "headline": "National Football Team Appoints New Manager After Tournament Exit",
            "summary": "Following their disappointing performance in the recent tournament, the national football association has named a new manager to lead the team."
        },
        {
            "headline": "Basketball Star Signs Record-Breaking Contract with New Team",
            "summary": "One of basketball's most celebrated players has agreed to a historic deal with a new team, becoming the highest-paid athlete in the league."
        },
        {
            "headline": "Tennis Grand Slam Introduces New Technology for Line Calls",
            "summary": "Tournament organizers have implemented advanced technology to replace human line judges, promising more accurate calls in professional tennis matches."
        },
        {
            "headline": "Sports Medicine Breakthrough Could Reduce Athlete Recovery Time",
            "summary": "Researchers have developed a new treatment protocol that significantly decreases recovery time for common sports injuries among professional athletes."
        }
    ]
}

class NewsCrawler(threading.Thread):
    """
    A simplified demo news crawler
    """
    def __init__(self, keyword=None, source_id=None):
        threading.Thread.__init__(self)
        self.keyword = keyword
        self.source_id = source_id
        
    def run(self):
        """Run the crawler in a separate thread"""
        # Get active sources
        if self.source_id:
            sources = NewsSource.objects.filter(is_active=True, id=self.source_id)
        else:
            sources = NewsSource.objects.filter(is_active=True)
        
        if not sources:
            print("No active sources found. Please add sources in the admin panel.")
            return
            
        # Simulate crawling by creating demo articles
        for source in sources:
            self.generate_articles(source)
                
    def generate_articles(self, source):
        """Generate sample articles for demo purposes"""
        # Number of articles to generate
        num_articles = random.randint(5, 10)
        
        # If we have a specific keyword template, use it
        if self.keyword and self.keyword.lower() in KEYWORD_TEMPLATES:
            templates = KEYWORD_TEMPLATES[self.keyword.lower()]
            
            # Generate articles from the keyword templates
            for template in templates:
                headline = template["headline"]
                summary = template["summary"]
                
                # Create a unique URL
                url = f"https://example.com/news/{hashlib.md5(headline.encode()).hexdigest()}"
                
                # Create content hash for deduplication
                content = (headline + summary).encode('utf-8')
                content_hash = hashlib.sha256(content).hexdigest()
                
                # Check if article already exists
                if not NewsArticle.objects.filter(content_hash=content_hash).exists():
                    try:
                        # Save to database
                        NewsArticle.objects.create(
                            source=source,
                            headline=headline,
                            summary=summary, 
                            url=url,
                            content_hash=content_hash
                        )
                        print(f"Generated article: {headline}")
                    except Exception as e:
                        print(f"Error saving article: {str(e)}")
            
            # Add a few more general articles with the keyword
            for _ in range(2):
                news = random.choice(SAMPLE_NEWS)
                headline = f"{self.keyword.capitalize()}: {news['headline']}"
                summary = f"This article about {self.keyword} discusses {news['summary'].lower()}"
                
                # Create a unique URL
                url = f"https://example.com/news/{hashlib.md5(headline.encode()).hexdigest()}"
                
                # Create content hash for deduplication
                content = (headline + summary).encode('utf-8')
                content_hash = hashlib.sha256(content).hexdigest()
                
                # Save if not a duplicate
                if not NewsArticle.objects.filter(content_hash=content_hash).exists():
                    try:
                        NewsArticle.objects.create(
                            source=source,
                            headline=headline,
                            summary=summary, 
                            url=url,
                            content_hash=content_hash
                        )
                        print(f"Generated article: {headline}")
                    except Exception as e:
                        print(f"Error saving article: {str(e)}")
                        
        else:
            # For unknown keywords or no keyword, generate standard articles
            for _ in range(num_articles):
                # Select a random news item from our samples
                news = random.choice(SAMPLE_NEWS)
                headline = news["headline"]
                summary = news["summary"]
                
                # If keyword is provided, include it in most articles
                if self.keyword:
                    # Create a more natural inclusion of the keyword
                    variations = [
                        f"{headline} ({self.keyword})",
                        f"{self.keyword} Impact: {headline}",
                        f"{headline}: What it Means for {self.keyword}",
                        headline.replace("New", f"New {self.keyword}")
                    ]
                    headline = random.choice(variations)
                    
                    # Add keyword to summary naturally
                    summary_variations = [
                        f"{summary} This development has significant implications for {self.keyword}.",
                        f"Experts in {self.keyword} have analyzed this situation: {summary}",
                        f"{summary} This could reshape the future of {self.keyword}.",
                        f"The {self.keyword} community has responded to this news: {summary}"
                    ]
                    summary = random.choice(summary_variations)
                
                # Create a unique URL
                url = f"https://example.com/news/{hashlib.md5(headline.encode()).hexdigest()}"
                
                # Create content hash for deduplication
                content = (headline + summary).encode('utf-8')
                content_hash = hashlib.sha256(content).hexdigest()
                
                # Check if article already exists
                if not NewsArticle.objects.filter(content_hash=content_hash).exists():
                    try:
                        # Save to database
                        NewsArticle.objects.create(
                            source=source,
                            headline=headline,
                            summary=summary, 
                            url=url,
                            content_hash=content_hash
                        )
                        print(f"Generated article: {headline}")
                    except Exception as e:
                        print(f"Error saving article: {str(e)}")

def run_crawler(keyword=None, source_id=None):
    """
    Run the crawler in a separate thread
    
    Args:
        keyword (str, optional): Keyword to search for
        source_id (int, optional): ID of source to crawl
    """
    crawler = NewsCrawler(keyword=keyword, source_id=source_id)
    crawler.daemon = True
    crawler.start()
    return "Crawler started"

if __name__ == "__main__":
    # For standalone testing
    run_crawler() 