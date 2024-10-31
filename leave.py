from src.login import LoginAutomation
from src.report import ReportAutomation
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tkinter as tk
from tkinter import ttk
import time
import logging

class LeaveAutomation(LoginAutomation):
    def __init__(self):
        super().__init__()
    
    # 퇴근 버튼 클릭
    def click_leave_button(self):
        try:
            leave_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "minCommuteInfo_offwork"))
            )
            leave_button.click()
            logging.info("퇴근 버튼 클릭 완료")
            
        except Exception as e:
            logging.error(f"퇴근 버튼 클릭 중 오류 발생: {str(e)}")
            raise e

class AutomationGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("업무보고•퇴근 자동화 프로그램")
        self.root.geometry("800x600")

        # 중앙 위치 설정
        window_width = 400
        window_height = 300

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")  # 중앙 위치로 설정
        
        # 프레임 생성
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 행과 열에 대한 가중치 설정
        self.frame.grid_rowconfigure(0, weight=1)  # 첫 번째 행에 가중치 추가
        self.frame.grid_columnconfigure(0, weight=1)  # 첫 번째 열에 가중치 추가
        
        self.leave_button = ttk.Button(self.frame, text="퇴근하기", command=self.leave_work)
        self.leave_button.grid(row=1, column=0, pady=10, sticky="nsew")
        # 퇴근하기 버튼 옆에 자동 실행 시간 레이블 추가
        self.leave_time_label = ttk.Label(self.frame, text="18:00에 자동 실행")
        self.leave_time_label.grid(row=1, column=1, pady=10, sticky="nsew")
        
        # 버튼들 생성
        self.start_button = ttk.Button(self.frame, text="업무보고", command=self.run_automation)
        self.start_button.grid(row=2, column=0, pady=10, sticky="nsew")
        # 업무보고 버튼 옆에 자동 실행 시간 레이블 추가
        self.report_time_label = ttk.Label(self.frame, text="17:40에 자동 실행")
        self.report_time_label.grid(row=2, column=1, pady=10, sticky="nsew")

        self.automation = None

        self.schedule_time = "17:40"  # 원하는 자동 실행 시간 설정 (예: 17:00)
        self.check_time()  # 시간 체크 시작

    def run_automation(self):
        try:
            if not self.automation:  # 자동화 객체가 없을 때만 생성
                self.automation = LeaveAutomation()
                self.automation.login()
            
            report = ReportAutomation(self.automation.driver)
            report.navigate_to_report()
            report_content = report.copy_previous_report();
            report.input_report_content(report_content)
            
            self.check_interval = 10000  # 업무보고 후 체크 주기를 10초로 변경
        except Exception as e:
            self.logger.error(f"업무보고 중 오류 발생: {str(e)}")

    def leave_work(self):
        try:
            # LeaveAutomation 객체가 없으면 새로 생성
            if not self.automation:
                self.automation = LeaveAutomation()
                self.automation.login()  # 로그인 수행

            self.automation.click_leave_button()  # 퇴근 버튼 클릭
        except Exception as e:
            self.logger.error(f"퇴근 처리 중 오류 발생: {str(e)}")

    def check_time(self):
        current_time = time.strftime("%H:%M")
        if current_time == self.schedule_time:
            self.run_automation()  # 자동으로 실행
            self.report_time_label.config(text="완료")  # 업무보고 완료 표시
        if current_time == "18:00":  # 6시가 되면
            self.leave_work()  # 퇴근 버튼 클릭
            self.leave_time_label.config(text="완료")  # 퇴근 완료 표시
        self.root.after(10000, self.check_time) # 일정시간마다 체크

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = AutomationGUI()
    gui.run()