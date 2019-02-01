import requests
import scrapy
import json
import webbrowser
import os
import sys

session = requests.session()

print("Enter Product Url")
product_url = input()
#product_url = "https://www.shoppersstop.com/p-204128165_9407/colorChange?colorCode=204128165_9407" #sample URL
csrf_url = "https://www.shoppersstop.com/getCSRFToken"
add_url = "https://www.shoppersstop.com/cart/add"
csrf_payload = ""

#Product Page
response = session.request("GET", product_url, data=csrf_payload)

#Extracting Product id and Size id
res = scrapy.Selector(text = response.text)
li = res.xpath(".//ul[@class='variant_size_ulClass']/li")

#Extract Product ID
pro = li.xpath(".//input[@class='variantSizeUrl']/@value").extract()[0]
productCode = pro.replace("/p-", "")

#Extract Size ID
sizeCodes = li.xpath(".//input[@id='variantSizeCode']/@value").extract()
buttons = li.xpath(".//button")

#Extract All Sizes
buttonValues = li.xpath(".//button/text()").extract()

#details[] contains all available Size and it's Size Code
details = []

#removing unavailable options
for i in range(len(sizeCodes)):
	item = []
	if not (buttons[i].xpath("./@disabled")):
		item.append(sizeCodes[i])
		item.append(buttonValues[i])
		details.append(item)

if not details:
	print("Out of Stock")
	sys.exit()

print ("Available Options")
i = 1
for item in details:
	print (str(i) + ". ", end=" ")
	print (item[1])
	i = i + 1

print ("Select the Size")
user_input = int(input())

itemCode = details[user_input - 1][0]

#Select Size Call
item_select_url = "https://www.shoppersstop.com/p-" + productCode + "/sizeChange"
querystring = {"sizeCode":itemCode,"pincode":""}
response_p = session.request("GET", item_select_url, data=csrf_payload, params=querystring)

#CSRF Call
response = session.request("GET", csrf_url, data=csrf_payload)
_csrf = response.text.strip().replace('"', '')

payload = "qty=1&baseProductCode=" + productCode + "&productCodePost=" + itemCode + "&CSRFToken=" + _csrf + "&undefined="

#add to cart Call
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
response_a = session.request("POST", add_url, data=payload, headers=headers)


#Cart Page
cart_url = "https://www.shoppersstop.com/cart"
headers = {'cache-control': "no-cache"}
response_c = session.request("GET", cart_url, data=csrf_payload)

#output cart.html
with open("cart.html", 'wb') as fd:
    for chunk in response_c.iter_content(chunk_size=128):
        fd.write(chunk)

print ("Item got added to Cart.")

#Open in Browser
webbrowser.open('file://' + os.path.realpath("cart.html"))