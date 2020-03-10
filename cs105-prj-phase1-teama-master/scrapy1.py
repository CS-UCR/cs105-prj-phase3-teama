import scrapy

class nbastatsSpider(scrapy.Spider):
    name = "nba_stats"
    
    start_urls = [
        'https://stats.nba.com'
    ]
    
    def parse(self, response):
        for href in response.css('.player + a::attr(href)'):
            yield response.follow(href, self.parse_player)
            
            
    def parse_player(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()
        
        
        yield {
            'name': extract_with_css('p.player-summary_first-name::text')
        }
        
