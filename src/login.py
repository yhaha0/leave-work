from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from dotenv import load_dotenv
import os
# from selenium.webdriver.chrome.options import Options

class LoginAutomation:
    def __init__(self):
        load_dotenv()
        self.setup_logging()
        self.LOGIN_URL = os.getenv('LOGIN_URL')
        self.USERID = os.getenv('USERID')
        self.PASSWORD = os.getenv('PASSWORD')
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def init_driver(self):
        # options = Options()
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # self.driver = webdriver.Chrome(options=options)

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)  # 브라우저가 자동으로 닫히지 않도록 설정
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        
    def login(self):
        try:
            self.init_driver()
            self.logger.info("브라우저를 시작합니다.")
            
            # 페이지 접속
            self.driver.get(self.LOGIN_URL)
            self.logger.info(f"{self.LOGIN_URL}에 접속했습니다.")
            
            # 로그인 정보 입력
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "cmmLogin_userId"))
            )
            username_field.send_keys(self.USERID)
            
            password_field = self.driver.find_element(By.ID, "cmmLogin_pwd")
            password_field.send_keys(self.PASSWORD)
            
            # 로그인 버튼 클릭
            login_button = self.driver.find_element(By.ID, "cmmLogin_login")
            login_button.click()
            
            self.logger.info("로그인 시도 완료")
            
        except Exception as e:
            self.logger.error(f"로그인 중 오류 발생: {str(e)}")
            self.driver.quit()  # 오류 발생시에만 브라우저 종료
            self.logger.info("오류로 인해 브라우저를 종료합니다.")
