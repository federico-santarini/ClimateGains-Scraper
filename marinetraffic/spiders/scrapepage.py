import scrapy
from scrapy.http.request import Request
import re
from  datetime import datetime

from ..items import vesselsInPort
from ..items import vesselDetails
from ..items import portsList


class portScraper(scrapy.Spider):
    """ Take a snapshot of vessels in Sabetta port """

    name = 'portScraper'
    start_urls = ['https://www.marinetraffic.com/en/ais/details/ports/21528']
    custom_settings = {
        'MONGO_DATABASE': 'SabettaPort',
        'ITEM_PIPELINES': { 'marinetraffic.pipelines.mongoLocalPipeline': 400,
                            'marinetraffic.pipelines.justArrivedPipeline': 300 

        }
    }

    def parse(self,response):

        items = vesselsInPort()

        # extract tables
        vessels_link = response.xpath('//*[@id="currvess"]/tbody/tr/td/a').extract()
        vessels_type = response.xpath('//*[@id="currvess"]/tbody/tr/td/img').extract()

        # Regex patterns
        nameRe = re.compile('(?<=\>)(.*?)(?=\<)')
        mmsiRe = re.compile('(?<=mmsi:)(.*)(?=/vessel)')
        imoRe = re.compile('(?<=imo:)(.*)(?=/mmsi)')
        typeRe = re.compile('(?<=title=")(.*)(?=">)')

        for i in range(10):
            name = nameRe.search(vessels_link[i])[0],
            mmsi = mmsiRe.search(vessels_link[i])[0],
            imo = imoRe.search(vessels_link[i])[0],
            link = "https://www.vesselfinder.com/?mmsi=" + mmsiRe.search(vessels_link[i])[0]

            vesselType = typeRe.search(vessels_type[i])[0]
            items['timestamp'] = datetime.now().strftime('%Y-%m-%d | %H:%M')
            items['name'] = name[0]
            items['mmsi'] = mmsi[0]
            items['imo'] = imo[0]
            items['link'] = link
            items['vesselType'] = vesselType

            yield items

class vesselScraper(scrapy.Spider):
    """ Scrape details of every Yamal icebrakers-tanker fleet """

    name = 'vesselScraper'
    start_urls = ['https://www.vesselfinder.com/vessels/CHRIS.-DE-MARGERIE-IMO-9737187-MMSI-212611000',
                  'https://www.vesselfinder.com/vessels/BORIS-VILKITSKY-IMO-9768368-MMSI-212654000',
                  'https://www.vesselfinder.com/vessels/VLADIMIR-RUSANOV-IMO-9750701-MMSI-477150100',
                  'https://www.vesselfinder.com/vessels/FEDOR-LITKE-IMO-9768370-MMSI-212660000',
                  'https://www.vesselfinder.com/vessels/EDUARD-TOLL-IMO-9750696-MMSI-311000548',
                  'https://www.vesselfinder.com/vessels/RUDOLF-SAMOYLOVICH-IMO-9750713-MMSI-311000627',
                  'https://www.vesselfinder.com/vessels/VLADIMIR-VIZE-IMO-9750658-MMSI-477194200',
                  'https://www.vesselfinder.com/vessels/GEORGIY-BRUSILOV-IMO-9768382-MMSI-212770000',
                  'https://www.vesselfinder.com/vessels/BORIS-DAVYDOV-IMO-9768394-MMSI-209356000',
                  'https://www.vesselfinder.com/vessels/NIKOLAY-ZUBOV-IMO-9768526-MMSI-209351000',
                  'https://www.vesselfinder.com/vessels/NIKOLAY-YEVGENOV-IMO-9750725-MMSI-311000631',
                  'https://www.vesselfinder.com/vessels/VLADIMIR-VORONIN-IMO-9750737-MMSI-311000632',
                  'https://www.vesselfinder.com/vessels/NIKOLAY-URVANTSEV-IMO-9750660-MMSI-477327300',
                  'https://www.vesselfinder.com/vessels/GEORGIY-USHAKOV-IMO-9750749-MMSI-311000633',
                  'https://www.vesselfinder.com/vessels/YAKOV-GAKKEL-IMO-9750672-MMSI-311000634'
                  ]
    custom_settings = {
        'MONGO_DATABASE': 'Vessels',
        'ITEM_PIPELINES': { 'marinetraffic.pipelines.mongoLocalPipeline': 400 }
    }

    def parse(self,response):

        # Items class inazialization
        items = vesselDetails()

        # Extraction from 'PORT CALLS' table
        try:
            port_dest = response.xpath('//*[@class="tparams npctable"]/tbody/tr/td/a/text()').extract()[1]
            country_dest = response.xpath('//*[@class="tparams npctable"]/tbody/tr/td/a/span/@title').extract()[0]
        except:
            port_dest = 'Unknown'
            country_dest = 'Unknown'

        # Extraction from 'POSITION & VOYAGE DATA' table
        details = response.xpath('//*[@class="tparams"]/tbody/tr/td[2]/text()').extract()

        name = details[13],
        imo = details[4].split()[0],
        mmsi = details[4].split()[2],
        countryDest = country_dest,
        portDest = port_dest.split()[0],
        flag = details[1],
        portCode = details[2],
        status = details[10]
        coordinates = { 'lat': details[9].split('/')[0].split()[0],
                        'lon': details[9].split('/')[1].split()[0] },

        items['name'] = name[0]
        items['flag'] = flag[0]
        items['imo'] = imo[0]
        items['mmsi'] = mmsi[0]
        items['portCode'] = portCode[0]
        items['countryDest'] = countryDest[0]
        items['portDest'] = portDest[0]
        items['status'] = status
        items['coordinates'] = coordinates[0]
        items['timestamp'] = datetime.now().strftime('%Y-%m-%d | %H:%M')


        yield items

class portListScraper(scrapy.Spider):
    """ Scrape a list of ports with country and locodes """

    name = "portListScraper"
    start_urls = ["https://www.vesselfinder.com/ports?page="]
    max_id = 316

    custom_settings = {
        'MONGO_DATABASE': 'WorldPortsList',
        'ITEM_PIPELINES': { 'marinetraffic.pipelines.mongoLocalPipeline': 400 }
    }


    def start_requests(self):
        for i in range(1, self.max_id):
            yield Request('https://www.vesselfinder.com/ports?page=%d' % i, callback = self.parse)

    def parse(self,response):

        items = portsList()

        # extract list with countries, ports, locodes
        countries = response.xpath('//*[@class="results table is-hoverable is-fullwidth"]/tbody/tr/td/div/a/*[@class="row-country"]/text()').extract()
        ports = response.xpath('//*[@class="results table is-hoverable is-fullwidth"]/tbody/tr/td/div/a/*[@class="row-title"]/text()').extract()
        locodes = response.xpath('//*[@class="results table is-hoverable is-fullwidth"]/tbody/tr/*[@class="v2"]/text()').extract()

        for i in range(len(countries)):
            items['country'] = countries[i]
            items['port'] = ports[i]
            items['locode'] = locodes[i]

            yield items
