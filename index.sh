#!/bin/bash
brew services start mongodb-community@3.6

# Activate env
source activate GeneralEnvironment

# Go to dir. and run spiders
cd /Users/federicosantarini/Scraper/marinetraffic
scrapy crawl vesselScraper
scrapy crawl portScraper

# Deactivate env
source deactivate GeneralEnvironment

brew services stop mongodb-community@3.6
