import requests

url = "https://ronreiter-meme-generator.p.rapidapi.com/meme"

querystring = {
    "top": "Top Text",
    "bottom": "Bottom Text",
    "meme": "Condescending-Wonka",
    "font_size": "50",
    "font": "Impact"
}

headers = {
    "X-RapidAPI-Key": "529db806d7mshf647499ca507ea4p1413edjsnd8e908396cc2",
    "X-RapidAPI-Host": "ronreiter-meme-generator.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    try:
        json_data = response.json()
        print(json_data)
    except requests.exceptions.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Raw response content:", response.content)
else:
    print("Request failed with status code:", response.status_code)
    print("Raw response content:", response.content)