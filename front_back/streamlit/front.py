import streamlit as st
import requests

# Streamlit页面设置
st.title('Flask & Streamlit 示例')

# 向Flask后端发送GET请求
response = requests.get('http://localhost:5000/api/test')
if response.status_code == 200:
    data = response.json()
    st.write(f"消息来自Flask: {data['message']}")
else:
    st.write("无法从Flask获取数据")

# streamlit run front.py