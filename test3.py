# -*- codeing = utf-8 -*-
# @Time : 2020/11/17 1:22
# @Author : Cj
# @File : test3.py
# @Software : PyCharm

import os,glob
def photo_compression(original_imgage,tmp_image_path):
    '''图片备份、压缩；param original_imgage:原始图片路径；param tmp_imgage_path:临时图片路径，备份路径；return'''
    from PIL import Image
    img = Image.open(original_imgage)
    width,height = img.size
    while (width*height>4000000):#该数值压缩后的图片大约200多k
        width = width//2
        height = height//2
    e_img = img.resize((width,height),Image.BILINEAR)
    save_path = os.path.join(tmp_image_path,os.path.basename(original_imgage))
    e_img.save(save_path)
    return save_path

def ocr(original_image):
    '''使用百度OCR进行文字识别，支持JPG、JPEG、PNG、BMP格式；param original_image:待识别图片；return'''
    from aip import AipOcr
    filename = os.path.basename(original_image)
    #输入自己的百度ai账号ID密码：参考链接：https://m.toutiaocdn.com/i6704242394566492684/
    APP_ID = '******'
    API_KEY = '*******'
    SECRECT_KEY = '*********'

    client = AipOcr(APP_ID,API_KEY,SECRECT_KEY)

    with open(original_image,'rb') as picfile_read:
        img = picfile_read.read()
        print('正在识别图片：{0}......'.format(filename))
        try:
            result = client.basicGeneral(img)#通用文字识别，50000次/天免费
        except:
            result = client.basicAccurate(img)#通用文字识别（高精度版），500次/天免费
    return result

def run_ocr(original_image,tmp_image_path,result_file_path='identify_results.txt'):
    '''主函数 批量执行图片文本识别，结果存储；original_image:原始图片；tmp_image_path:临时图片；result_file_path:识别文字存储文件；return'''

    if os.path.exists(result_file_path):#判断是否存在历史识别结果，若存在则删除
        os.remove(result_file_path)
    if not os.path.exists(tmp_image_path):#判断临时图片路径是否存在，若不存在则创建
        os.mkdir(tmp_image_path)
    tmp_file_path = []#临时文件路径列表
    for picfile in glob.glob(original_image):#glob.glob的参数是一个只含有方括号、问号、正斜线的正则表达式
        tmp_file = photo_compression(picfile,tmp_image_path)
        tmp_file_path.append(tmp_file)
    for picfile in tmp_file_path:#遍历所有文件，进行OCR识别 结果存储
        result = ocr(picfile)
        lines = [text.get('words') + '\n' for text in result.get('words_result')]
        # lines = [text.get('words').encode('utf-8')+'\n' for text in result.get('words_result')]

        with open(result_file_path,'a+',encoding='utf-8') as fo:
            fo.writelines("="*100+'\n')
            fo.writelines("【识别图片】：{0} \n".format(os.path.basename(picfile)))
            fo.writelines("【文本内容】： \n")
            fo.writelines(lines)
        os.remove(picfile)

if __name__ == '__main__':
    tmp_image_path = os.getcwd()+'\\tmp'
    original_image = os.getcwd() + '\\*.png'
    run_ocr(original_image,tmp_image_path)