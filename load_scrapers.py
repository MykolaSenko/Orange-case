from Scraper import Scraper
import time

# Override filter for specific demands
class Tel_packs(Scraper):
    def filter(self,objs):
        ret = []
        options = ['internet', 'mobiel', 'tv']
        for obj in objs:
            contains = any([option in obj.get_attribute('href') for option in options])
            if contains:
                ret.append(obj)
        return ret

if __name__ == '__main__':
    start = time.perf_counter()
    #tel = Tel_packs('tel_packs')
    #tel.run()
    #tel_promo = Scraper('tel_promo')
    #tel_promo.run()
    tel_promo = Scraper('mobilevk')
    tel_promo.run()

    end = time.perf_counter()
    print(end-start)