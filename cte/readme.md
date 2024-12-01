# cte一般路径

## 代码移植-python
```python
img_file="test.jpg"
dev_id=0
handle = sail.Handle(dev_id)
decoder = sail.Decoder(img_file, True, dev_id)
bmimg = sail.BMImage()
decoder.read(handle, bmimg)    
```

bool isAlignWidth = false;
float ratio = get_aspect_scaled_ratio(images.width, images.height, m_net_w, m_net_h, &isAlignWidth);
bmcv_padding_atrr_t padding_attr;
memset(&padding_attr, 0, sizeof(padding_attr));
padding_attr.dst_crop_sty = 0;
padding_attr.dst_crop_stx = 0;
padding_attr.padding_b = 114;
padding_attr.padding_g = 114;
padding_attr.padding_r = 114;
padding_attr.if_memset = 1;
if (isAlignWidth) {
    padding_attr.dst_crop_h = images.height*ratio;
    padding_attr.dst_crop_w = m_net_w;

    int ty1 = (int)((m_net_h - padding_attr.dst_crop_h) / 2);
    padding_attr.dst_crop_sty = ty1;
    padding_attr.dst_crop_stx = 0;
}else{
    padding_attr.dst_crop_h = m_net_h;
    padding_attr.dst_crop_w = images.width*ratio;

    int tx1 = (int)((m_net_w - padding_attr.dst_crop_w) / 2);
    padding_attr.dst_crop_sty = 0;
    padding_attr.dst_crop_stx = tx1;
}

bmcv_rect_t crop_rect{0, 0, images.width, images.height};
auto ret = bmcv_image_vpp_convert_padding(m_bmContext->handle(), 1, images, &m_resized_imgs,
    &padding_attr, &crop_rect, BMCV_INTER_NEAREST);

auto ret = bmcv_image_vpp_convert(m_bmContext->handle(), 1, images, &m_resized_imgs);