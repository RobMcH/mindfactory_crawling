# Mindfactory.de Crawler
This repository contains a crawler for [Mindfactory](https://www.mindfactory.de), a German eCommerce shop (for computer hardware).
The crawler extracts the data contained on every single product page and stores the scraped products and reviews in a SQLite database consisting of two tables.  

Each product has the following properties:  
* ID (SQLite identifier)
* URL
* Product name
* Brand name
* Category (i.e. CPU)
* EAN
* SKU
* Items sold (count)
* People watching (count)
* RMA quote (in percent)
* Average rating (from 1.0 to 5.0)
* Shipping (information on availability)
* Price (in Euro)  

Additionally, for every product all reviews are collected and stored in a separate SQLite table. An entry in this table has the following properties:
* Product ID (reference to the corresponding ID in the product table)
* Stars (rating, from 1 to 5)
* Text (not tokenized/pre-processed in any kind)
* Author
* Date (YYYY-MM-DD)
* Verified (if the customer actually bought the product at Mindfactory)

# Prerequisites  
* Python 3 (>= 3.5)
* scrapy (>= 1.6.0)
* SQLite3

# Run the scraper  
    scrapy crawl mindfactory_products
    
# Deploy the scraper
The scraper can be deployed using scrapyd. In order to do that, just run [scrapyd-deploy](https://github.com/scrapy/scrapyd-client#scrapyd-deploy)
with the address to the server running scrapyd. Afterwards the scraper can be used with scrapyd.

    python scrapyd-deploy    
