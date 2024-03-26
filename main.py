import json
import requests_html
from abc import ABC, abstractmethod


class BaseParser(ABC):

    def __init__(self, url: str, query=None) -> None:  # ссылка и параметр
        self._url = url
        self._query = query
        self._session = requests_html.HTMLSession()
        self._get_page()
        
    
    def _get_page(self):  # запро на всю страницу 
        self.response = self._session.get(self._url)
        if self.response.status_code == 200:
            return self.response
        print(f"ERR - {self.response}")


    def get_page_query(self, num):  # запро на всю страницу c определенным параметром
        __response_query = self._session.get(self._url+self._query+f"{num}")
        if __response_query.status_code == 200:
            return __response_query
        print(f"ERR - {__response_query}")

    def get_new_page(self, new_url):
        self.response_new = self._session.get(new_url)
        if self.response_new.status_code == 200:
            return self.response_new
        print(f"ERR - {self.response_new}")
            

    def write(self, name_file: str, wr_file):  # запись в файл
        with open(f"{name_file}.json", "w+") as file:
            json.dump(wr_file, file, indent=4, ensure_ascii=False)


    @abstractmethod
    def _full_list_html(self):
        pass


    @abstractmethod
    def start(self):
        pass


    @abstractmethod
    def save(self):
        pass
        


class AntaresAvtoJp(BaseParser):

    def _full_list_html(self): # отпредилил количество страниц
        _all_element_list = []
        __page = self.response
        __last_num_page = __page.html.find(".pagination li:last-child", first=True)
        __all_num = int(__last_num_page.text)

        for num in range(1, __all_num+1):  # сбор всех нужных элементов с каждой страции в один список 
            __num_page = self.get_page_query(num)
            __items_list = __num_page.html.find("#content .car-list .car-plate")
            _all_element_list.extend(__items_list)
        self._all_params_card(_all_element_list)
            

    def _all_params_card(self, _all_element_list):  # запись всех значений с сайта в список
        self._resalt = []
        __number = 0 
    
        for _el in _all_element_list:
            __el_name = self._get_name(_el)
            __el_year = self._get_year(_el)
            __el_specifications = self._get_specifications(_el)
            __number +=1
            self._resalt.append({"№": __number, "name": __el_name, "years": __el_year, "specifications": __el_specifications})


    def _get_name(self, _el):  # получение данных товара
        _name = _el.find(".car-list-name  a", first=True)  
    
        return _name.text


    def _get_year(self, _el):  # получение данных товара
        _years = _el.find(".car-list-data  a", first=True)
    
        return _years.text.replace("\xa0", "")
    

    def _get_specifications(self, _el):  # получение данных товара
        _storege = []
        __all_characteristics = _el.find(".row-car .col-data-small:nth-child(3) .car-list-param")
        for __item in __all_characteristics:
            __car_param = __item.find("div", first=True)
            _storege.append(__car_param.text)
        return _storege
    

    def start(self):
        self._full_list_html()


    def save(self):
        __name = "INFO_AntaresAvtoJP"        
        self.write(__name, self._resalt)
        print(f"\033[30;42mИнформация загружена в файл {__name}\033[0m")


class Gismeteo(BaseParser):

    def _full_list_html(self): # получаем список всех элементов с нужной информацией 
        __page = self.response
        _all_element_list = __page.html.find(".row-item")
        self._all_params_card(_all_element_list)
            

    def _all_params_card(self, _all_element_list):  # запись всех значений с сайта в список
        self._resalt = []
    
        for _el in _all_element_list:
            __el_day = self._get_day(_el)
            __el_max = self._get_max(_el)
            __el_min = self._get_min(_el)
            
            self._resalt.append({"day": __el_day, "max_t": __el_max, "min_t": __el_min})


    def _get_day(self, _el):  # получение данных товара
        _day = _el.find(".date", first=True) 
    
        return _day.text.replace("\xa0"," ")


    def _get_max(self, _el):  # получение данных товара
        _max = _el.find(".temp .maxt .unit_temperature_c", first=True)
    
        return _max.text.replace("\xa0"," ")
    

    def _get_min(self, _el):  # получение данных товара
        _min = _el.find(".temp .mint .unit_temperature_c", first=True)
    
        return _min.text.replace("\xa0"," ")


    def start(self):
        self._full_list_html()


    def save(self):
        __name = "INFO_Gismeteo"        
        self.write(__name, self._resalt)
        print(f"\033[30;42mИнформация загружена в файл {__name}\033[0m")



class KinoAfisha(BaseParser):

    def _full_list_html(self): # все сылки на страници с информацией
        __page = self.response
        __links_list = __page.html.find("#site .grid_cell9 .movieList .grid_cell4 a.movieItem_title")
        _full_links = []

        for __title in __links_list:  # сбор всех сылок в список 
            _full_links.extend(__title.absolute_links)
        self._every_request(_full_links)
 

    def _every_request(self, _full_links):  # заходи на каждую страницу и указываем отправную точку
        self._resalt = []
        for new_url in _full_links:  # заходим в каждую ссылку и забираем инфу  
            self.get_new_page(new_url)
            __page_now = self.response_new
            _all_element_list = __page_now.html.find("#site .filmSection", first=True)
            self._all_params_card(_all_element_list)
 

    def _all_params_card(self, _el):  # запись всех значений с сайтов в список
        __el_name = self._get_name(_el)
        __el_rating = self._get_rating(_el)
        __el_description = self._get_description(_el)
        __el_info = self._get_extended_info(_el)
        __el_about_film = self._get_about_film(_el)
        
        self._resalt.append({"name": __el_name, "rating": __el_rating, "description": __el_description, "info": __el_info, "about_film": __el_about_film})
        

    def _get_name(self, _el):  # получение данных товара
        _name = _el.find(".trailer-popup .trailer_headerTop .trailer_headerInfo h1", first=True) 
    
        return _name.text


    def _get_rating(self, _el):  # получение данных товара
        try:
            _rating = _el.find(".trailer-popup .trailer_headerFrame :nth-child(2) .rating_stat .imdbRatingPlugin", first=True)
            return _rating.text
        except AttributeError:
            return "Рейтинг IMDb: -"
        

    def _get_description(self, _el):  # получение данных товара
        try:
            _description = _el.find(".filmSection_shortDesc.column-width", first=True)
            return _description.text
        except AttributeError:
            return "-"
        

    def _get_extended_info(self, _el):  # получение данных товара
        __info = _el.find(".column-width .tab_inner .grid_cell9 .filmInfo_info .filmInfo_infoItem")
        _conteyner = {}
        for __item in __info:
            __key = __item.find(".filmInfo_infoName", first=True)
            __val = __item.find(".filmInfo_infoData", first=True)
            _conteyner[f"{__key.text}"] = f"{__val.text}"
            
        return _conteyner
    

    def _get_about_film(self, _el):  # получение данных товара
        _about_film = _el.find(".column-width .tab_inner .grid_cell9 .gamma-main .tabs_contentList p", first=True)

        return _about_film.text.replace("\xa0"," ")
    

    def start(self):
        self._full_list_html()


    def save(self):
        __name = "INFO_KinoAfisha"         
        self.write(__name, self._resalt)
        print(f"\033[30;42mИнформация загружена в файл {__name}\033[0m")



if __name__ == "__main__":
    avto_jp = AntaresAvtoJp("https://antaresjp.ru/aukciony/honda/civic/", query="?pagen=") 
    avto_jp.start()
    avto_jp.save()
    gis = Gismeteo("https://www.gismeteo.ru/weather-tyumen-4501/month/")
    gis.start()
    gis.save()
    kino = KinoAfisha("https://tmn.kinoafisha.info/movies/")
    kino.start()
    kino.save()
