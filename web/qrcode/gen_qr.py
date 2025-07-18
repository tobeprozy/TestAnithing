import qrcode

# 要转换为二维码的链接
url = "https://www.baidu.com/"

# 创建二维码
qr = qrcode.QRCode(
    version=1,  # 控制二维码的大小，1是最小的大小
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # 控制二维码的纠错级别
    box_size=10,  # 控制二维码中每个方块的大小
    border=4,  # 控制二维码边框的宽度
)

# 添加数据到二维码
qr.add_data(url)
qr.make(fit=True)

# 创建二维码图像
img = qr.make_image(fill='black', back_color='white')

# 保存二维码图像
img.save("qixi_qrcode.png")