import matplotlib.pyplot as plt
import numpy as np

# 数据
years = ['2019', '2020', '2021', '2022', '2023', '2024 (估计)', '2025 (估计)', '2026 (估计)', '2027 (估计)', '2028 (估计)']
china_market = [2.4, 7.4, 13.9, 19.4, 27.0, 39.7, 54.5, 68.8, 83.1, 92.5]
global_market = [3.4, 10.1, 8.7, 14.1, 21.7, 30.6, 39.0, 44.7, 49.6, 0]  # 2028年全球数据缺失

# 创建图表
fig, ax = plt.subplots(2, 1, figsize=(10, 8))

# 绘制柱状图
ax[0].bar(years, china_market, label='中国', color='blue', alpha=0.7)
ax[0].bar(years, global_market, label='全球', color='gray', alpha=0.7)
ax[0].set_title('市场规模 (人民币十亿元)')
ax[0].set_xlabel('年份')
ax[0].set_ylabel('市场规模 (人民币十亿元)')
ax[0].legend()
ax[0].grid(True)

# 绘制复合年增长率表格
cagr_data = [
    ['中国', '55.5%', '28.6%'],
    ['全球', '38.6%', '27.5%']
]
cagr_table = ax[1].table(cellText=cagr_data, colLabels=['地区', '2019年至2023年', '2023年至2030年 (估计)'], loc='center')
ax[1].set_title('复合年增长率')
ax[1].axis('off')  # 隐藏坐标轴

# 调整布局
plt.tight_layout()

# 保存图表为 PNG 文件
plt.savefig('market_growth.png', dpi=300, bbox_inches='tight')

# 显示图表
plt.show()