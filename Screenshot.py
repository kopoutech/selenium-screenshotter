from selenium import webdriver
import json
import re
import math

from PIL import Image



driver:webdriver.Chrome = None
screen_size = (1024 , 768 )
url = "http://127.0.0.1:3000/webdesign"

def load_driver(url):
  global driver
  driver = webdriver.Chrome(executable_path = 'F:/bin/chromedriver.exe')
  driver.get(url)
  print("Original Window size",driver.get_window_size())

def set_viewport_size(width, height):
    # window_size = driver.execute_script("""
    #     return [window.outerWidth - window.innerWidth + arguments[0],
    #       window.outerHeight - window.innerHeight + arguments[1]];
    #     """, width, height)
    # driver.set_window_size(*window_size)
    driver.set_window_position(0,0)
    driver.set_window_size(width, height)

def screenshot_with_size(screen_size):
  
  image_name = f"web_url_{screen_size[0]}x{screen_size[1]}_"
  set_viewport_size(screen_size[0], screen_size[1])
  page_height = driver.execute_script("return document.body.scrollHeight")
  screen_height = driver.get_window_size()["height"]
  print(f"current page height: {page_height} | window size {driver.get_window_size()} | expected_screen_size: {screen_size} ")

  images_saved = []
  meta = {
    "window_size" : (driver.get_window_size()["width"], driver.get_window_size()["height"]),
    "page_height" : page_height,
    "page_width" : driver.get_window_size()["width"],
    "filename" : f"{image_name}.png"
  }
  for i in range(math.ceil(page_height/screen_height)):
    q = f"window.scrollTo(0, {i*screen_height})"
    print(q)
    driver.execute_script(q) 
    filename = f'tmp/{image_name}_{i}.png'
    driver.save_screenshot(filename)
    images_saved.append(filename)
  
  meta["last_scroll_position"] = driver.execute_script("return window.pageYOffset")
  return images_saved, meta

def parseScreenSize(sizeString):
  result = re.search("^([0-9]+)[ ]*x[ ]*([0-9]+)", sizeString)
  print(result.groups())
  return result.groups()

def image_stitch(images, meta):
    """Merge two images into one, displayed side by side
    :param file1: path to first image file
    :param file2: path to second image file
    :return: the merged Image object
    """

    image_list = [Image.open(f) for f in images]
    image_len = len(image_list)
    if image_len == 1:
      image_list[0].save(f"final/{meta['filename']}")
      return image_list[0]
    
    im_height = image_list[0].size[1]
    im_width = image_list[0].size[0]
    result_width = image_list[0].size[0]
    result_height = image_len * image_list[0].size[1]

    result = Image.new('RGB', (result_width, result_height))
    
    # print(meta, image_list[0].size)
    for index, im in enumerate(image_list):
      if index == image_len - 1: # last image
        diff_y = im.size[1]- meta["last_scroll_position"] #im.size[1]-
        crop_box = (
          0,
          diff_y,
          im.size[0],
          im.size[1]
        )
        # print(index, box)
        im=im.crop(
          crop_box
        ) 
      box = (0, 
              index * im_height,
              im.size[0],
              index * im_height + im.size[1]
              )
      result.paste(im=im, box=box)
    result.save(f"final/{meta['filename']}")
    return result

def load_json_manifest(filename):
  with open(filename, "r") as fp:
    data = fp.read()
  data = json.loads(data)

  viewed_screen_sizes = []
  for device in data:
    if device["ScreenSize"] not in viewed_screen_sizes:
      screen_size = parseScreenSize(device["ScreenSize"])
      image_name = f"web_url_{screen_size[0]}x{screen_size[1]}_"
      print(image_name)
      images, meta = screenshot_with_size(screen_size)
      image_stitch(images, meta)
    
    # break

def defaults():
  import os
  import shutil
  shutil.rmtree('tmp')
  os.makedirs("tmp")
  os.makedirs("final", exist_ok=True)

defaults()
load_driver(url)
load_json_manifest("ios.json")