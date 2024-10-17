import time
import urllib.request
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

search_query = input(f"찾고싶은 사람 이름을 입력하세요: ")

options = Options()
# 자동 닫힘 안되게
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
# 창 최대화
driver.maximize_window()

url = "https://images.google.com/"
driver.get(url)

# 모두 로드 될때까지 최대 10초 대기
wait = WebDriverWait(driver, 10)
elem = driver.find_element(By.NAME, "q")

elem.send_keys(search_query)
elem.send_keys(Keys.RETURN)
time.sleep(2)

# 사용자 지정 폴더 경로 설정
custom_path = "C:/Users/kimmc/PycharmProjects/Animal_Face/"

# 폴더 생성 (사용자 지정 경로에 검색어 이름으로)
save_path = os.path.join(custom_path, search_query)
if not os.path.exists(save_path):
    os.makedirs(save_path)

# 스크롤 끝까지 내리기
def scroll_down(driver, scroll_pause_time=1, max_scrolls=10):
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0

    while scrolls < max_scrolls:
        # 페이지 끝까지 스크롤 다운
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 페이지 로드 대기
        time.sleep(scroll_pause_time)

        # 스크롤 후 새로운 높이 계산
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # 더 이상 로드할 내용이 없으면 중단

        last_height = new_height
        scrolls += 1

# 스크롤 다운 실행
scroll_down(driver, scroll_pause_time=2, max_scrolls=10)
time.sleep(2)

image_urls = []
small_images = driver.find_elements(By.CSS_SELECTOR, ".YQ4gaf")
# 진짜 큰 사진들만 필터링
real_images = [img for img in small_images if img.get_attribute("class") == "YQ4gaf"]
max_images = 50

for i, real_image in enumerate(real_images[:max_images]):
    try:
        # 스크롤하여 이미지 위치 조정 (이미지를 화면에 완전히 보이도록 함)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", real_image)
        time.sleep(1)  # 스크롤 후 로딩 시간 대기

        # 작은 이미지 클릭 (클릭이 인터셉트될 수 있으므로 JavaScript로 클릭 시도)
        driver.execute_script("arguments[0].click();", real_image)

        # 확대된 이미지가 로딩될 때까지 대기
        expanded_image = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sFlh5c.FyHeAf.iPVvYb")))

        # 확대된 이미지의 src 속성 가져오기 (User-Agent 헤더 사용) - 403 forbidden 피하기 위해
        image_src = expanded_image.get_attribute("src")
        req = urllib.request.Request(image_src, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

        if image_src and image_src.startswith('http'):
            image_urls.append(image_src)
            with urllib.request.urlopen(req) as response, open(os.path.join(save_path, f"{i}.jpg"), 'wb') as out_file:
                out_file.write(response.read())  # 이미지 저장
            print(f"이미지 {i} 저장 완료!: {image_src}")

        # 이미지 로딩 및 클릭 간 시간 지연을 위해 대기
        time.sleep(1)

    except Exception as e:
        print(f"이미지 처리 중 오류 발생: {e}")
