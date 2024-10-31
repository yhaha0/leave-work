import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os
from dotenv import load_dotenv

class ReportAutomation:
    def __init__(self, driver):
        load_dotenv()
        self.driver = driver
        self.logger = self._setup_logger()
        self.NAME = os.getenv('NAME')
        self.DEPARTMENT = os.getenv('DEPARTMENT')
        self.receivers = os.getenv('RECEIVERS', '').split(',')
    
    def _setup_logger(self):
        logger = logging.getLogger('ReportAutomation')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
        
        return logger
    
    def navigate_to_report(self):
        try:
            # 업무보고 메뉴 클릭
            report_menu = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "publish_lnb_fe2589250161000052"))
            )
            report_menu.click()
            self.logger.info("업무보고 메뉴 클릭")
            
        except Exception as e:
            self.logger.error(f"업무보고 페이지 이동 중 오류 발생: {str(e)}")
            raise

    def copy_previous_report(self):
        try:
            # 첫 번째 nowrap_txt_inline div 요소를 찾아서 클릭
            first_report = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.nowrap_txt_inline"))
            )
            first_report.click()
            
            # repReportView_content의 내용을 가져오기
            report_content = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "repReportView_content"))
            )
            
            # 내용 선택을 위해 JavaScript 실행
            select_script = """
            const content = document.getElementById('repReportView_content');
            const range = document.createRange();
            range.selectNodeContents(content);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            """
            self.driver.execute_script(select_script)
            
            # Ctrl+C 작 실행
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
            
            self.logger.info("전날 보고 내용 복사 완료")
            
            return report_content.text
        except Exception as e:
            self.logger.error(f"전날 보고 내용 복사 중 오류 발생: {str(e)}")
            raise

    def input_report_content(self, content):
        try:
            # 보고 작성 버튼 클릭
            write_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "repLeft_btnWriteReport"))
            )
            write_button.click()
            self.logger.info("보고 작성 버튼 클릭")

            # 제목 입력
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")

            title_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "repReportEdit_reportWriteTitle"))
            )
            title_input.clear()
            title_input.send_keys(f"{today} / {self.NAME} / {self.DEPARTMENT}")
            self.logger.info("보고서 제목 입력 및 내용 붙여넣기 완료")

            # 첫 번째 iframe에 접근
            first_iframe = WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "iframe__DOC_CONTENT_"))
            )
            self.logger.info("첫 번째 iframe에 접근 완료")

            # 두 번째 iframe으로 전환
            second_iframe = WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "dext_frame_editor1"))
            )
            self.logger.info("두 번째 iframe에 접근 완료")

            # 세 번째 iframe으로 전환
            third_iframe = WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "dext5_design_editor1"))
            )
            self.logger.info("세 번째 iframe에 접근 완료")
            
            editor_body = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            editor_body.send_keys(content)
            
            # 기본 프레임으로 복귀
            self.driver.switch_to.default_content()


            # 수신자 입력
            receiver_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.input_zone textarea#publish_repReportEdit_writeReportRecipient_textarea"))
            )
            
            for receiver in self.receivers:
                if not receiver.strip():  # 빈 문자열 건너뛰기
                    continue
                
                receiver_input.send_keys(receiver.strip())
                time.sleep(0.1)  # 자동완성 목록 로딩 대기
                
                # 자동완성 목록에서 항목 선택
                focused_item = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-menu-item"))
                )
                focused_item.click()
                time.sleep(0.1)  # 다음 입력을 위한 대기
                
            self.logger.info("모든 수신자 입력 완료")
            
        except Exception as e:
            self.logger.error(f"에디터 입력 중 오류 발생: {str(e)}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            raise