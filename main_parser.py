import requests
from bs4 import BeautifulSoup
import time
import json

def improvement_text(text):
    text = text.replace("  ", "").replace("\n", "")
    return text

def pars_main_page():

    def connect_to_url():

        headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 YaBrowser/21.2.2.102 Yowser/2.5 Safari/537.36"}
        url = "https://www.eatthismuch.com/food/browse/?type=recipe"
        res = requests.get(url, headers = headers).text

        with open("main_page_for_site.html", "w+", encoding = "utf-8") as file:
            file.write(res)

    def pars_catigories():

        with open("main_page_for_site.html", "r", encoding = "utf-8") as file:
            html_code = file.read()

        soup = BeautifulSoup(html_code, "html.parser")
        main_tag = soup.find("div", class_ = "recipe_type_categories")

        catigories_text_list = []
        catigories_list = main_tag.find_all("li", class_ = "nav-item")

        flag = 0
        for improvement_text_items in catigories_list:

            if flag > 0:

                text_for_tag = improvement_text(improvement_text_items.text)
                catigories_text_list.append(text_for_tag)

            flag += 1
        return catigories_text_list

    connect_to_url()
    catigories_list = pars_catigories()
    return catigories_list

#парсинг рецептов и их ингридиентов по категориям и по страницам
def pars_recipes_for_ingredients_in_catigories_and_pages(catigories_list):

    def connect_url_in_iteration_for_catigories(catigories_list):
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 YaBrowser/21.2.2.102 Yowser/2.5 Safari/537.36"}

        for catigory in catigories_list:
            time.sleep(5)
            page = 0
            url = "https://www.eatthismuch.com/food/browse/?type=recipe"
            print(catigory)

            while True:

                page += 1
                params = {"group":catigory, "page":page}

                try:
                    res = requests.get(url, headers = headers, params = params)
                except:
                    time.sleep(300)
                    continue

                status_code = res.status_code
                res_text = res.text
                print("статус", status_code)
                print("страница", page)
                if status_code == 400:
                    break

                elif status_code == 429:
                    time.sleep(300)
                    continue

                with open("page_catigory.html", "w+", encoding = "utf-8") as file:
                    file.write(res_text)

                print("Парсинг html рецептов...")
                print("Рецепты спарсились")
                pars_html_recipes(catigory)
                time.sleep(3)
    #парсинг html рецептов
    def pars_html_recipes(catigory):
        with open("page_catigory.html", "r", encoding = "utf-8") as file:
            html_code = file.read()

        soup = BeautifulSoup(html_code, "html.parser")
        main = soup.find_all("div", class_ = "row food_result")

        dict_for_recipe_json = {}

        for item in main:
            name = item.find("div", class_ = "result_name col-3").text
            name = improvement_text(name)

            calories = item.find("div", class_ = "col-2 offset-1 nutrient_cell").text
            calories = improvement_text(calories)

            calories_tag = item.find("div", class_ = "col-2 nutrient_cell")

            fats = calories_tag.find_next_sibling().text
            fats = improvement_text(fats)

            fats_tag_for_next_sibling = calories_tag.find_next_sibling()

            proteins = fats_tag_for_next_sibling.find_next_sibling().text
            proteins = improvement_text(proteins)

            carbs = item.find("div", class_ = "col-2 nutrient_cell").text
            carbs = improvement_text(carbs)

            dict_for_recipe_json = {"Catigory":catigory, "Name":name, "Calories":calories, "Fats":fats, "Proteins":proteins, "Carbs":carbs}

            save_file = open("recipes.json", "a", encoding = "utf-8")
            save_file.write(json.dumps(dict_for_recipe_json))

    connect_url_in_iteration_for_catigories(catigories_list)
    pars_html_recipes()

catigories_list = pars_main_page()
pars_recipes_for_ingredients_in_catigories_and_pages(catigories_list)
