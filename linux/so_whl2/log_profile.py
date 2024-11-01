
from bs4 import BeautifulSoup

from pyecharts.charts import Bar, Page, Line
from pyecharts import options as opts
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts

def get_perf_bar(
    operators_list:list, device_time_cost: dict, chart_title: str, chart_id: str
):
    print("Generating performance bar...")

def get_perf_table(operators_list:list, device_time_cost: dict):
    print("Generating performance table...")

def get_perf_line(
    device_usage_data: dict,
    date_time_data: list,
    chart_id: str,
    title_str:str,
    axis_opts: dict,
):
    print("Generating performance line...")

def analyze_log(log_data:str):
    print("Analyzing log...")

def get_time_per_operator(operators_info: dict):
    print("Calculating time per operator...")

def get_average_time(total_time_cost_per_device: dict, operators_list: list):
    print("Calculating average time...")

def re_render_page(html_path:str, task_name:str):
    print("Rendering page...")

def get_algo_perf_page(algo_perf_log: str, task_name: str):
    print("Generating performance page...")