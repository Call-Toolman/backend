def city2list(city):
    city_list = city.split('-')
    return city_list


def list2city(city_list):
    str = '-'
    city =str.join(city_list)
    return city 

if __name__ == '__main__':
    city = "beijing-beijing-haidian"
    city_list = city2list(city)
    print(city_list)
    print(list2city(city_list))
