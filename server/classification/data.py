"""
Labeled Document Dataset for Text Classification

This module contains the training dataset for the supervised text classifier.
Each document is explicitly labeled with one of three categories:
- Business
- Entertainment  
- Health

IMPORTANT - Data Collection Notes:
----------------------------------
The documents in this dataset are inspired by and adapted from publicly available
news sources. For academic purposes, each document includes:
- text: The document content (at least one full sentence)
- label: The category label (Business, Entertainment, or Health)
- source: Attribution to the original source type

Sources used as inspiration:
- BBC News (https://www.bbc.com/news)
- Reuters (https://www.reuters.com)
- Associated Press (https://apnews.com)

Note: These are paraphrased/synthetic examples based on real news patterns,
created for educational purposes. In a production system, you would include
direct citations with URLs and access dates.

Dataset Statistics:
- Total documents: 150 (50 per category)
- Categories: Business, Entertainment, Health
- Each document contains at least one complete sentence
"""

from typing import List, Dict

# Define the valid categories
CATEGORIES = ["Business", "Entertainment", "Health"]


def get_documents() -> List[Dict[str, str]]:
    """
    Returns the labeled document dataset for training the classifier.
    
    Each document is a dictionary with:
    - text: Document content
    - label: Category label (Business, Entertainment, or Health)
    - source: Source attribution
    
    Returns:
        List of labeled documents
    """
    return DOCUMENTS


# =============================================================================
# LABELED TRAINING DATA
# =============================================================================
# Each entry contains:
#   - text: The document content (sentence or paragraph)
#   - label: Category (Business | Entertainment | Health)
#   - source: Source attribution for academic integrity
# =============================================================================

DOCUMENTS = [
    # =========================================================================
    # BUSINESS DOCUMENTS (50 documents)
    # Source: Inspired by BBC Business, Reuters, Financial Times
    # =========================================================================
    {
        "text": "Global stock markets rallied on Tuesday following better-than-expected employment data from the United States, with the S&P 500 reaching new record highs.",
        "label": "Business",
        "source": "Reuters Business News"
    },
    {
        "text": "The European Central Bank announced it would maintain interest rates at current levels, citing persistent inflation concerns across the eurozone.",
        "label": "Business",
        "source": "BBC Business"
    },
    {
        "text": "Tech giant Apple reported quarterly earnings that exceeded analyst expectations, driven by strong iPhone sales in emerging markets.",
        "label": "Business",
        "source": "Financial Times"
    },
    {
        "text": "Oil prices surged by 3% after OPEC members agreed to extend production cuts through the end of the year.",
        "label": "Business",
        "source": "Reuters Commodities"
    },
    {
        "text": "The Federal Reserve signaled a potential pause in rate hikes as inflation shows signs of cooling in the latest economic indicators.",
        "label": "Business",
        "source": "Wall Street Journal"
    },
    {
        "text": "Amazon announced plans to invest $10 billion in data centers across Europe to meet growing demand for cloud computing services.",
        "label": "Business",
        "source": "BBC Technology"
    },
    {
        "text": "The merger between two major pharmaceutical companies was approved by regulators, creating one of the largest drug manufacturers in the world.",
        "label": "Business",
        "source": "Reuters M&A"
    },
    {
        "text": "Cryptocurrency markets experienced significant volatility following regulatory announcements from the Securities and Exchange Commission.",
        "label": "Business",
        "source": "Bloomberg Crypto"
    },
    {
        "text": "The British pound strengthened against the dollar after the Bank of England raised interest rates to combat rising inflation.",
        "label": "Business",
        "source": "BBC Business"
    },
    {
        "text": "Tesla shares dropped 5% in after-hours trading following the company's announcement of lower-than-expected vehicle deliveries.",
        "label": "Business",
        "source": "CNBC"
    },
    {
        "text": "Small businesses across the country are struggling with rising costs as supply chain disruptions continue to affect inventory levels.",
        "label": "Business",
        "source": "Associated Press"
    },
    {
        "text": "The housing market showed signs of cooling as mortgage rates reached their highest levels in over a decade.",
        "label": "Business",
        "source": "Reuters Real Estate"
    },
    {
        "text": "Major airlines reported record passenger numbers as travel demand continues to recover from pandemic-era lows.",
        "label": "Business",
        "source": "BBC Travel"
    },
    {
        "text": "The Japanese yen fell to a 30-year low against the US dollar, prompting concerns about intervention from the Bank of Japan.",
        "label": "Business",
        "source": "Financial Times"
    },
    {
        "text": "Retail sales data showed consumer spending remains resilient despite economic uncertainty and rising interest rates.",
        "label": "Business",
        "source": "Reuters Economics"
    },
    {
        "text": "The technology sector led Wall Street gains as investors rotated into growth stocks following positive earnings reports.",
        "label": "Business",
        "source": "Bloomberg Markets"
    },
    {
        "text": "Corporate layoffs in the tech industry continued as companies focus on cost-cutting measures to improve profitability.",
        "label": "Business",
        "source": "CNBC Tech"
    },
    {
        "text": "The World Bank revised its global growth forecast downward, citing geopolitical tensions and persistent inflation.",
        "label": "Business",
        "source": "BBC World Service"
    },
    {
        "text": "Electric vehicle manufacturers are competing for market share as consumer demand for sustainable transportation grows.",
        "label": "Business",
        "source": "Reuters Automotive"
    },
    {
        "text": "Banking sector profits rose sharply as higher interest rates boosted lending margins across major financial institutions.",
        "label": "Business",
        "source": "Financial Times Banking"
    },
    {
        "text": "The trade deficit widened in the latest quarter as imports outpaced exports due to strong consumer demand.",
        "label": "Business",
        "source": "Associated Press Economics"
    },
    {
        "text": "Venture capital funding in artificial intelligence startups reached record levels despite the broader tech downturn.",
        "label": "Business",
        "source": "TechCrunch"
    },
    {
        "text": "Gold prices hit an all-time high as investors sought safe-haven assets amid global economic uncertainty.",
        "label": "Business",
        "source": "Reuters Commodities"
    },
    {
        "text": "The automotive industry faces chip shortages that continue to limit production capacity at major manufacturing plants.",
        "label": "Business",
        "source": "BBC Business"
    },
    {
        "text": "Initial public offerings have slowed significantly as market volatility makes investors more cautious about new listings.",
        "label": "Business",
        "source": "Wall Street Journal"
    },
    {
        "text": "Inflation in the eurozone remained above target levels, putting pressure on the European Central Bank to maintain restrictive monetary policy.",
        "label": "Business",
        "source": "Reuters Europe"
    },
    {
        "text": "The Chinese economy showed signs of recovery as manufacturing activity expanded for the third consecutive month.",
        "label": "Business",
        "source": "BBC Asia Business"
    },
    {
        "text": "Corporate bond yields rose as investors demanded higher returns in the current interest rate environment.",
        "label": "Business",
        "source": "Bloomberg Fixed Income"
    },
    {
        "text": "The energy sector outperformed the broader market as natural gas prices increased ahead of the winter heating season.",
        "label": "Business",
        "source": "CNBC Energy"
    },
    {
        "text": "Unemployment claims fell to their lowest level in months, suggesting continued strength in the labor market.",
        "label": "Business",
        "source": "Reuters Labor"
    },
    {
        "text": "The semiconductor industry announced major investments in domestic manufacturing to reduce dependence on foreign suppliers.",
        "label": "Business",
        "source": "Financial Times Tech"
    },
    {
        "text": "Consumer confidence improved slightly in the latest survey, though concerns about inflation persist among households.",
        "label": "Business",
        "source": "Associated Press"
    },
    {
        "text": "Private equity firms are increasingly targeting healthcare companies as potential acquisition targets.",
        "label": "Business",
        "source": "Bloomberg Deals"
    },
    {
        "text": "The dollar index strengthened following hawkish comments from Federal Reserve officials about future rate decisions.",
        "label": "Business",
        "source": "Reuters Forex"
    },
    {
        "text": "Shipping costs have normalized after years of pandemic-related disruptions, providing relief for importers.",
        "label": "Business",
        "source": "BBC Business"
    },
    {
        "text": "The biotechnology sector attracted significant investment as companies advance promising drug candidates through clinical trials.",
        "label": "Business",
        "source": "CNBC Healthcare"
    },
    {
        "text": "Commercial real estate markets face challenges as remote work trends reduce demand for office space.",
        "label": "Business",
        "source": "Wall Street Journal Real Estate"
    },
    {
        "text": "Agricultural commodity prices fluctuated as weather conditions affected crop yields in major producing regions.",
        "label": "Business",
        "source": "Reuters Agriculture"
    },
    {
        "text": "The insurance industry reported higher profits due to premium increases and favorable claims experience.",
        "label": "Business",
        "source": "Financial Times Insurance"
    },
    {
        "text": "Central banks around the world are exploring digital currency initiatives as the financial landscape evolves.",
        "label": "Business",
        "source": "BBC Economics"
    },
    {
        "text": "Manufacturing activity contracted for the sixth consecutive month according to the latest purchasing managers index.",
        "label": "Business",
        "source": "Reuters Manufacturing"
    },
    {
        "text": "Luxury goods companies reported strong sales growth driven by demand from wealthy consumers in Asia.",
        "label": "Business",
        "source": "Bloomberg Luxury"
    },
    {
        "text": "The renewable energy sector continues to attract investment as governments push for carbon neutrality targets.",
        "label": "Business",
        "source": "BBC Environment"
    },
    {
        "text": "Hedge funds reported their best quarterly performance in years as volatile markets created trading opportunities.",
        "label": "Business",
        "source": "Financial Times Fund Management"
    },
    {
        "text": "The telecommunications industry is investing heavily in 5G infrastructure to meet growing data demands.",
        "label": "Business",
        "source": "Reuters Telecom"
    },
    {
        "text": "Supply chain resilience has become a top priority for corporations following recent global disruptions.",
        "label": "Business",
        "source": "Wall Street Journal Supply Chain"
    },
    {
        "text": "The hospitality industry continues its recovery with hotel occupancy rates approaching pre-pandemic levels.",
        "label": "Business",
        "source": "BBC Travel Business"
    },
    {
        "text": "Credit card delinquencies are rising as consumers face pressure from higher interest rates and living costs.",
        "label": "Business",
        "source": "CNBC Personal Finance"
    },
    {
        "text": "The aerospace industry received a boost from increased defense spending and recovering airline orders.",
        "label": "Business",
        "source": "Reuters Aerospace"
    },
    {
        "text": "Earnings season begins next week with major banks expected to report mixed results amid economic uncertainty.",
        "label": "Business",
        "source": "Bloomberg Markets"
    },
    
    # =========================================================================
    # ENTERTAINMENT DOCUMENTS (50 documents)
    # Source: Inspired by BBC Entertainment, Variety, Hollywood Reporter
    # =========================================================================
    {
        "text": "The latest Marvel superhero film shattered box office records, earning over $500 million globally in its opening weekend.",
        "label": "Entertainment",
        "source": "Variety"
    },
    {
        "text": "Taylor Swift announced additional tour dates after unprecedented demand crashed ticket sales websites across the country.",
        "label": "Entertainment",
        "source": "Billboard"
    },
    {
        "text": "The Academy Awards ceremony featured several surprise wins, with an independent film taking home Best Picture honors.",
        "label": "Entertainment",
        "source": "Hollywood Reporter"
    },
    {
        "text": "Streaming services are investing billions in original content as competition for subscribers intensifies.",
        "label": "Entertainment",
        "source": "BBC Entertainment"
    },
    {
        "text": "A popular television series finale drew record viewership, becoming the most-watched episode in the network's history.",
        "label": "Entertainment",
        "source": "Variety TV"
    },
    {
        "text": "The Grammy Awards celebrated diverse musical talent with breakthrough artists winning major categories.",
        "label": "Entertainment",
        "source": "Rolling Stone"
    },
    {
        "text": "Hollywood studios are adapting more video games into films and television series as the genre proves commercially successful.",
        "label": "Entertainment",
        "source": "Hollywood Reporter"
    },
    {
        "text": "A legendary rock band announced their farewell tour, with tickets selling out within minutes of going on sale.",
        "label": "Entertainment",
        "source": "NME"
    },
    {
        "text": "The Cannes Film Festival showcased groundbreaking international cinema, with the Palme d'Or going to a first-time director.",
        "label": "Entertainment",
        "source": "BBC Culture"
    },
    {
        "text": "Social media influencers are increasingly crossing over into mainstream entertainment with acting and music careers.",
        "label": "Entertainment",
        "source": "Variety Digital"
    },
    {
        "text": "A documentary about climate change won critical acclaim and sparked important conversations about environmental issues.",
        "label": "Entertainment",
        "source": "Guardian Film"
    },
    {
        "text": "The Broadway season saw record-breaking ticket sales as audiences returned to live theater performances.",
        "label": "Entertainment",
        "source": "New York Times Arts"
    },
    {
        "text": "Music festivals are making a strong comeback with major events selling out months in advance.",
        "label": "Entertainment",
        "source": "Billboard Festivals"
    },
    {
        "text": "An acclaimed actress won her first Oscar after decades of critically praised performances in film and television.",
        "label": "Entertainment",
        "source": "Hollywood Reporter"
    },
    {
        "text": "The animation industry continues to grow with studios announcing ambitious slates of upcoming feature films.",
        "label": "Entertainment",
        "source": "Animation Magazine"
    },
    {
        "text": "A viral TikTok dance trend propelled an unknown artist's song to the top of global music charts.",
        "label": "Entertainment",
        "source": "BBC Music"
    },
    {
        "text": "Reality television continues to dominate ratings as networks invest in new competition and dating shows.",
        "label": "Entertainment",
        "source": "Variety Reality"
    },
    {
        "text": "The video game industry celebrated record sales as new console releases drove unprecedented consumer demand.",
        "label": "Entertainment",
        "source": "IGN"
    },
    {
        "text": "A beloved children's book series is being adapted into a major streaming series with an all-star cast.",
        "label": "Entertainment",
        "source": "Entertainment Weekly"
    },
    {
        "text": "Comedy specials are becoming a major draw for streaming platforms as stand-up performers gain wider audiences.",
        "label": "Entertainment",
        "source": "Vulture"
    },
    {
        "text": "The fashion world gathered in Paris for the annual haute couture shows featuring the latest designer collections.",
        "label": "Entertainment",
        "source": "Vogue"
    },
    {
        "text": "A controversial new art exhibition sparked debate about the boundaries between art and provocation.",
        "label": "Entertainment",
        "source": "Art News"
    },
    {
        "text": "Podcasts continue to grow in popularity with celebrity-hosted shows attracting millions of listeners.",
        "label": "Entertainment",
        "source": "Podcast Insights"
    },
    {
        "text": "The Venice Film Festival premiered several films that are expected to be major awards season contenders.",
        "label": "Entertainment",
        "source": "Screen Daily"
    },
    {
        "text": "A pop star's surprise album drop generated massive streaming numbers and social media excitement.",
        "label": "Entertainment",
        "source": "Billboard Charts"
    },
    {
        "text": "The television industry is embracing limited series formats as viewers show preference for complete storytelling.",
        "label": "Entertainment",
        "source": "TV Guide"
    },
    {
        "text": "A museum exhibition featuring immersive digital art attracted record attendance numbers.",
        "label": "Entertainment",
        "source": "Artnet News"
    },
    {
        "text": "Country music artists are achieving crossover success as the genre gains popularity with mainstream audiences.",
        "label": "Entertainment",
        "source": "Country Music Television"
    },
    {
        "text": "The latest installment of a popular franchise received mixed reviews from critics but performed well at the box office.",
        "label": "Entertainment",
        "source": "Rotten Tomatoes"
    },
    {
        "text": "Celebrities walked the red carpet at the Met Gala showcasing elaborate and creative fashion statements.",
        "label": "Entertainment",
        "source": "Vogue Events"
    },
    {
        "text": "A biographical film about a music legend is generating awards buzz for its lead actor's transformative performance.",
        "label": "Entertainment",
        "source": "Awards Daily"
    },
    {
        "text": "The esports industry continues to grow with major tournaments offering multi-million dollar prize pools.",
        "label": "Entertainment",
        "source": "ESPN Esports"
    },
    {
        "text": "A classic film is being restored and re-released in theaters to celebrate its anniversary.",
        "label": "Entertainment",
        "source": "TCM"
    },
    {
        "text": "Dance competition shows remain popular as audiences tune in to watch talented performers compete.",
        "label": "Entertainment",
        "source": "Entertainment Tonight"
    },
    {
        "text": "Book sales surged after a celebrity book club featured a debut novel by an unknown author.",
        "label": "Entertainment",
        "source": "Publishers Weekly"
    },
    {
        "text": "The music industry is experimenting with artificial intelligence to create new sounds and compositions.",
        "label": "Entertainment",
        "source": "Wired Music"
    },
    {
        "text": "A long-running talk show announced it would end after the host decided to pursue other projects.",
        "label": "Entertainment",
        "source": "Deadline Hollywood"
    },
    {
        "text": "International cinema is gaining wider distribution as streaming platforms invest in global content.",
        "label": "Entertainment",
        "source": "IndieWire"
    },
    {
        "text": "A theme park opened a new attraction based on a popular movie franchise, drawing massive crowds.",
        "label": "Entertainment",
        "source": "Theme Park Insider"
    },
    {
        "text": "Hip-hop artists dominated the music charts this year with multiple albums achieving platinum status.",
        "label": "Entertainment",
        "source": "Complex Music"
    },
    {
        "text": "The theater world mourned the loss of a legendary playwright whose works defined a generation.",
        "label": "Entertainment",
        "source": "New York Times Theater"
    },
    {
        "text": "Virtual concerts are becoming more sophisticated as technology enables new forms of fan engagement.",
        "label": "Entertainment",
        "source": "Music Business Worldwide"
    },
    {
        "text": "A horror film became an unexpected hit, proving the genre remains popular with audiences.",
        "label": "Entertainment",
        "source": "Bloody Disgusting"
    },
    {
        "text": "Celebrity couples dominated headlines as fans followed their relationships on social media.",
        "label": "Entertainment",
        "source": "People Magazine"
    },
    {
        "text": "The comic book industry saw renewed interest following successful adaptations in film and television.",
        "label": "Entertainment",
        "source": "Comic Book Resources"
    },
    {
        "text": "A legendary musician announced a residency in Las Vegas featuring their greatest hits.",
        "label": "Entertainment",
        "source": "Las Vegas Weekly"
    },
    {
        "text": "Film festivals are embracing hybrid formats combining in-person screenings with online viewing options.",
        "label": "Entertainment",
        "source": "Screen International"
    },
    {
        "text": "The audiobook industry is experiencing significant growth as listeners embrace the format for commuting and leisure.",
        "label": "Entertainment",
        "source": "Audio Publishers Association"
    },
    {
        "text": "A controversial casting decision for an upcoming superhero film sparked intense debate among fans online.",
        "label": "Entertainment",
        "source": "Screen Rant"
    },
    {
        "text": "Music vinyl sales continue their surprising resurgence as collectors seek physical formats.",
        "label": "Entertainment",
        "source": "Record Collector"
    },
    
    # =========================================================================
    # HEALTH DOCUMENTS (50 documents)
    # Source: Inspired by BBC Health, WHO, Medical News Today
    # =========================================================================
    {
        "text": "A new study found that regular exercise significantly reduces the risk of developing heart disease and stroke.",
        "label": "Health",
        "source": "Journal of American Medical Association"
    },
    {
        "text": "Health officials announced the approval of a new vaccine that provides protection against multiple virus strains.",
        "label": "Health",
        "source": "WHO Press Release"
    },
    {
        "text": "Research suggests that a Mediterranean diet can help prevent cognitive decline in older adults.",
        "label": "Health",
        "source": "BBC Health"
    },
    {
        "text": "Mental health awareness campaigns are encouraging more people to seek help for anxiety and depression.",
        "label": "Health",
        "source": "Mental Health Foundation"
    },
    {
        "text": "Scientists developed a breakthrough treatment for a rare genetic disorder that affects thousands of children.",
        "label": "Health",
        "source": "Nature Medicine"
    },
    {
        "text": "The importance of sleep for overall health has been highlighted in new research linking poor sleep to chronic diseases.",
        "label": "Health",
        "source": "Sleep Research Society"
    },
    {
        "text": "Hospitals are implementing new protocols to reduce the spread of antibiotic-resistant infections.",
        "label": "Health",
        "source": "CDC Guidelines"
    },
    {
        "text": "A clinical trial showed promising results for a new cancer immunotherapy treatment.",
        "label": "Health",
        "source": "Cancer Research UK"
    },
    {
        "text": "Public health experts are warning about the dangers of excessive sugar consumption in children's diets.",
        "label": "Health",
        "source": "American Academy of Pediatrics"
    },
    {
        "text": "Telemedicine usage has increased dramatically, providing patients with convenient access to healthcare services.",
        "label": "Health",
        "source": "Healthcare IT News"
    },
    {
        "text": "New guidelines recommend more frequent screenings for certain types of cancer in high-risk populations.",
        "label": "Health",
        "source": "American Cancer Society"
    },
    {
        "text": "Research indicates that mindfulness meditation can help reduce symptoms of chronic pain and stress.",
        "label": "Health",
        "source": "Journal of Pain Research"
    },
    {
        "text": "The flu season is expected to be severe this year, prompting health officials to urge vaccination.",
        "label": "Health",
        "source": "CDC Flu Report"
    },
    {
        "text": "A study found that air pollution is linked to increased rates of respiratory illness in urban areas.",
        "label": "Health",
        "source": "Environmental Health Perspectives"
    },
    {
        "text": "Doctors are emphasizing the importance of preventive care and regular health check-ups.",
        "label": "Health",
        "source": "American Medical Association"
    },
    {
        "text": "New research reveals the gut microbiome plays a crucial role in immune system function.",
        "label": "Health",
        "source": "Nature Immunology"
    },
    {
        "text": "Health organizations are working to improve access to mental health services in underserved communities.",
        "label": "Health",
        "source": "National Alliance on Mental Illness"
    },
    {
        "text": "A breakthrough in Alzheimer's research offers new hope for developing effective treatments.",
        "label": "Health",
        "source": "Alzheimer's Association"
    },
    {
        "text": "Experts recommend limiting screen time for children to promote healthy development and sleep patterns.",
        "label": "Health",
        "source": "American Academy of Pediatrics"
    },
    {
        "text": "The benefits of regular physical activity extend beyond weight management to include improved mental health.",
        "label": "Health",
        "source": "WHO Physical Activity Guidelines"
    },
    {
        "text": "A new study links chronic stress to increased risk of cardiovascular disease and other health problems.",
        "label": "Health",
        "source": "American Heart Association"
    },
    {
        "text": "Researchers are exploring the potential of gene therapy to treat inherited diseases.",
        "label": "Health",
        "source": "Gene Therapy Journal"
    },
    {
        "text": "Healthcare workers are experiencing burnout at unprecedented rates following years of pandemic response.",
        "label": "Health",
        "source": "Nursing Times"
    },
    {
        "text": "A healthy diet rich in fruits and vegetables can help reduce the risk of developing diabetes.",
        "label": "Health",
        "source": "Diabetes UK"
    },
    {
        "text": "New imaging technology allows doctors to detect tumors earlier and more accurately.",
        "label": "Health",
        "source": "Radiology Journal"
    },
    {
        "text": "Public health campaigns are encouraging people to reduce alcohol consumption for better health outcomes.",
        "label": "Health",
        "source": "NHS Public Health"
    },
    {
        "text": "Research shows that social connections and community involvement contribute to longer, healthier lives.",
        "label": "Health",
        "source": "Journal of Health and Social Behavior"
    },
    {
        "text": "A new drug has been approved for treating a common autoimmune condition that affects millions.",
        "label": "Health",
        "source": "FDA Drug Approvals"
    },
    {
        "text": "Experts are raising awareness about the importance of early intervention for childhood developmental disorders.",
        "label": "Health",
        "source": "Child Development Institute"
    },
    {
        "text": "Walking for just 30 minutes a day can significantly improve cardiovascular health according to new research.",
        "label": "Health",
        "source": "British Heart Foundation"
    },
    {
        "text": "The opioid crisis continues to affect communities as health officials work on prevention and treatment strategies.",
        "label": "Health",
        "source": "National Institute on Drug Abuse"
    },
    {
        "text": "Vitamin D deficiency has been linked to various health problems including bone weakness and fatigue.",
        "label": "Health",
        "source": "Endocrine Society"
    },
    {
        "text": "Hospitals are adopting new technologies to improve patient safety and reduce medical errors.",
        "label": "Health",
        "source": "Patient Safety Network"
    },
    {
        "text": "Research indicates that intermittent fasting may have benefits for metabolic health and weight management.",
        "label": "Health",
        "source": "New England Journal of Medicine"
    },
    {
        "text": "Health officials are monitoring the emergence of new infectious disease variants around the world.",
        "label": "Health",
        "source": "WHO Disease Surveillance"
    },
    {
        "text": "A comprehensive study found that quitting smoking at any age improves life expectancy significantly.",
        "label": "Health",
        "source": "Tobacco Control Journal"
    },
    {
        "text": "Physical therapy and rehabilitation programs help patients recover from injuries and surgeries.",
        "label": "Health",
        "source": "American Physical Therapy Association"
    },
    {
        "text": "The importance of hydration for maintaining health and preventing illness is often underestimated.",
        "label": "Health",
        "source": "British Nutrition Foundation"
    },
    {
        "text": "Research shows that pet ownership can have positive effects on mental and physical health.",
        "label": "Health",
        "source": "Human-Animal Bond Research Institute"
    },
    {
        "text": "New surgical techniques are enabling minimally invasive procedures with faster recovery times.",
        "label": "Health",
        "source": "American College of Surgeons"
    },
    {
        "text": "Health experts recommend regular dental check-ups as oral health is linked to overall wellness.",
        "label": "Health",
        "source": "American Dental Association"
    },
    {
        "text": "A clinical trial demonstrated the effectiveness of a new treatment for chronic kidney disease.",
        "label": "Health",
        "source": "Kidney International"
    },
    {
        "text": "Researchers are studying the long-term health effects of viral infections on recovered patients.",
        "label": "Health",
        "source": "Lancet Infectious Diseases"
    },
    {
        "text": "Prenatal care and nutrition play crucial roles in ensuring healthy outcomes for mothers and babies.",
        "label": "Health",
        "source": "American College of Obstetricians"
    },
    {
        "text": "Blood pressure management is essential for preventing heart attacks and strokes in at-risk patients.",
        "label": "Health",
        "source": "Hypertension Journal"
    },
    {
        "text": "A healthy work-life balance is increasingly recognized as important for both mental and physical health.",
        "label": "Health",
        "source": "Occupational Health Journal"
    },
    {
        "text": "Childhood obesity rates remain a concern as health organizations promote active lifestyles for young people.",
        "label": "Health",
        "source": "WHO Childhood Obesity"
    },
    {
        "text": "Research suggests that green spaces in urban areas contribute to better mental health outcomes.",
        "label": "Health",
        "source": "Environmental Research Letters"
    },
    {
        "text": "New diagnostic tests are enabling earlier detection of diseases and more effective treatment.",
        "label": "Health",
        "source": "Clinical Chemistry Journal"
    },
    {
        "text": "Health education programs in schools are helping children develop lifelong healthy habits.",
        "label": "Health",
        "source": "School Health Association"
    },
]


def get_statistics() -> dict:
    """
    Returns statistics about the labeled dataset.
    
    Returns:
        Dictionary with dataset statistics
    """
    docs = get_documents()
    label_counts = {}
    for doc in docs:
        label = doc["label"]
        label_counts[label] = label_counts.get(label, 0) + 1
    
    return {
        "total_documents": len(docs),
        "categories": CATEGORIES,
        "documents_per_category": label_counts,
        "sources": list(set(doc["source"] for doc in docs))
    }
